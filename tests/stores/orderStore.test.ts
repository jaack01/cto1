import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  useOrderStore,
  resetOrderStore,
  computeStats,
  orderApi,
  type Order,
  type NewOrderPayload,
  type OrderStats,
} from '@/stores/orderStore';

describe('orderStore', () => {
  beforeEach(() => {
    resetOrderStore();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('computeStats', () => {
    it('returns zeroed stats for an empty array', () => {
      const result = computeStats([]);

      expect(result).toEqual({
        totalOrders: 0,
        pendingOrders: 0,
        readyOrders: 0,
        completedOrders: 0,
        totalRevenue: 0,
      });
    });

    it('tallies orders by status and sums revenue', () => {
      const orders: Order[] = [
        {
          id: '1',
          customerName: 'Alice',
          customerEmail: 'alice@example.com',
          itemDescription: 'Wash & Fold',
          quantity: 2,
          pricePerItem: 10,
          totalPrice: 20,
          status: 'pending',
          createdAt: '2024-03-01',
          updatedAt: '2024-03-01',
        },
        {
          id: '2',
          customerName: 'Bob',
          customerEmail: 'bob@example.com',
          itemDescription: 'Dry Cleaning',
          quantity: 1,
          pricePerItem: 35,
          totalPrice: 35,
          status: 'ready',
          createdAt: '2024-03-01',
          updatedAt: '2024-03-01',
          readyAt: '2024-03-01',
        },
        {
          id: '3',
          customerName: 'Charlie',
          customerEmail: 'charlie@example.com',
          itemDescription: 'Alterations',
          quantity: 1,
          pricePerItem: 25,
          totalPrice: 25,
          status: 'completed',
          createdAt: '2024-03-01',
          updatedAt: '2024-03-01',
          readyAt: '2024-03-01',
        },
      ];

      const result = computeStats(orders);

      expect(result).toEqual({
        totalOrders: 3,
        pendingOrders: 1,
        readyOrders: 1,
        completedOrders: 1,
        totalRevenue: 80,
      });
    });

    it('correctly groups multiple orders with same status', () => {
      const orders: Order[] = [
        {
          id: '1',
          customerName: 'Test 1',
          customerEmail: 'test1@example.com',
          itemDescription: 'Service A',
          quantity: 1,
          pricePerItem: 10,
          totalPrice: 10,
          status: 'ready',
          createdAt: '2024-03-01',
          updatedAt: '2024-03-01',
          readyAt: '2024-03-01',
        },
        {
          id: '2',
          customerName: 'Test 2',
          customerEmail: 'test2@example.com',
          itemDescription: 'Service B',
          quantity: 1,
          pricePerItem: 20,
          totalPrice: 20,
          status: 'ready',
          createdAt: '2024-03-01',
          updatedAt: '2024-03-01',
          readyAt: '2024-03-01',
        },
      ];

      const result = computeStats(orders);

      expect(result.totalOrders).toBe(2);
      expect(result.readyOrders).toBe(2);
      expect(result.pendingOrders).toBe(0);
      expect(result.completedOrders).toBe(0);
      expect(result.totalRevenue).toBe(30);
    });
  });

  describe('fetchOrders action', () => {
    it('sets loading true, fetches orders, then sets loading false', async () => {
      const mockOrders: Order[] = [
        {
          id: '1',
          customerName: 'Alice',
          customerEmail: 'alice@example.com',
          itemDescription: 'Laundry',
          quantity: 1,
          pricePerItem: 15,
          totalPrice: 15,
          status: 'pending',
          createdAt: '2024-03-01',
          updatedAt: '2024-03-01',
        },
      ];

      const mockFetcher = vi.fn(async () => mockOrders);

      const { fetchOrders } = useOrderStore.getState();
      const fetchPromise = fetchOrders(mockFetcher);

      expect(useOrderStore.getState().isLoading).toBe(true);

      await fetchPromise;

      expect(useOrderStore.getState().isLoading).toBe(false);
      expect(useOrderStore.getState().orders).toEqual(mockOrders);
      expect(useOrderStore.getState().stats.totalOrders).toBe(1);
      expect(mockFetcher).toHaveBeenCalledTimes(1);
    });

    it('updates the error state if the fetcher rejects', async () => {
      const mockFetcher = vi.fn(async () => {
        throw new Error('API unavailable');
      });

      const { fetchOrders } = useOrderStore.getState();
      await fetchOrders(mockFetcher);

      const state = useOrderStore.getState();
      expect(state.error).toBe('API unavailable');
      expect(state.isLoading).toBe(false);
      expect(state.orders).toEqual([]);
    });

    it('uses orderApi.fetchOrders by default', async () => {
      const mockOrders: Order[] = [
        {
          id: '100',
          customerName: 'Default API Order',
          customerEmail: 'api@example.com',
          itemDescription: 'Mock service',
          quantity: 1,
          pricePerItem: 20,
          totalPrice: 20,
          status: 'pending',
          createdAt: '2024-03-01',
          updatedAt: '2024-03-01',
        },
      ];

      vi.spyOn(orderApi, 'fetchOrders').mockResolvedValue(mockOrders);

      const { fetchOrders } = useOrderStore.getState();
      await fetchOrders();

      expect(orderApi.fetchOrders).toHaveBeenCalled();
      expect(useOrderStore.getState().orders).toEqual(mockOrders);
    });
  });

  describe('addOrder action', () => {
    it('creates an order and adds it to the orders list', async () => {
      const payload: NewOrderPayload = {
        customerName: 'Carol',
        customerEmail: 'carol@example.com',
        itemDescription: 'Ironing',
        quantity: 3,
        pricePerItem: 5,
      };

      const mockCreatedOrder: Order = {
        id: '42',
        ...payload,
        totalPrice: 15,
        status: 'pending',
        createdAt: '2024-03-01',
        updatedAt: '2024-03-01',
      };

      const mockCreator = vi.fn(async () => mockCreatedOrder);

      const { addOrder } = useOrderStore.getState();
      await addOrder(payload, mockCreator);

      const state = useOrderStore.getState();
      expect(state.orders).toHaveLength(1);
      expect(state.orders[0]).toEqual(mockCreatedOrder);
      expect(state.stats.totalOrders).toBe(1);
      expect(mockCreator).toHaveBeenCalledWith(payload);
    });

    it('sets error if the creator rejects', async () => {
      const payload: NewOrderPayload = {
        customerName: 'Test',
        customerEmail: 'test@example.com',
        itemDescription: 'Service',
        quantity: 1,
        pricePerItem: 10,
      };

      const mockCreator = vi.fn(async () => {
        throw new Error('Creation failed');
      });

      const { addOrder } = useOrderStore.getState();
      await addOrder(payload, mockCreator);

      const state = useOrderStore.getState();
      expect(state.error).toBe('Creation failed');
      expect(state.isLoading).toBe(false);
      expect(state.orders).toHaveLength(0);
    });

    it('uses orderApi.createOrder by default', async () => {
      const payload: NewOrderPayload = {
        customerName: 'Dave',
        customerEmail: 'dave@example.com',
        itemDescription: 'Dry Cleaning',
        quantity: 2,
        pricePerItem: 15,
      };

      const mockCreatedOrder: Order = {
        id: '999',
        ...payload,
        totalPrice: 30,
        status: 'pending',
        createdAt: '2024-03-01',
        updatedAt: '2024-03-01',
      };

      vi.spyOn(orderApi, 'createOrder').mockResolvedValue(mockCreatedOrder);

      const { addOrder } = useOrderStore.getState();
      await addOrder(payload);

      expect(orderApi.createOrder).toHaveBeenCalledWith(payload);
      expect(useOrderStore.getState().orders).toHaveLength(1);
    });
  });

  describe('updateOrderStatus action', () => {
    it('updates the status of an existing order', () => {
      const existingOrder: Order = {
        id: '10',
        customerName: 'Eve',
        customerEmail: 'eve@example.com',
        itemDescription: 'Laundry',
        quantity: 1,
        pricePerItem: 12,
        totalPrice: 12,
        status: 'pending',
        createdAt: '2024-03-01T10:00:00.000Z',
        updatedAt: '2024-03-01T10:00:00.000Z',
      };

      useOrderStore.setState({
        orders: [existingOrder],
        stats: computeStats([existingOrder]),
      });

      const { updateOrderStatus } = useOrderStore.getState();
      updateOrderStatus('10', 'ready');

      const state = useOrderStore.getState();
      expect(state.orders[0].status).toBe('ready');
      expect(state.orders[0].readyAt).toBeDefined();
      expect(state.stats.readyOrders).toBe(1);
      expect(state.stats.pendingOrders).toBe(0);
    });

    it('does not modify orders with different IDs', () => {
      const order1: Order = {
        id: '1',
        customerName: 'Frank',
        customerEmail: 'frank@example.com',
        itemDescription: 'Wash & Fold',
        quantity: 1,
        pricePerItem: 10,
        totalPrice: 10,
        status: 'pending',
        createdAt: '2024-03-01',
        updatedAt: '2024-03-01',
      };

      const order2: Order = {
        id: '2',
        customerName: 'Grace',
        customerEmail: 'grace@example.com',
        itemDescription: 'Dry Cleaning',
        quantity: 1,
        pricePerItem: 20,
        totalPrice: 20,
        status: 'pending',
        createdAt: '2024-03-01',
        updatedAt: '2024-03-01',
      };

      useOrderStore.setState({
        orders: [order1, order2],
        stats: computeStats([order1, order2]),
      });

      const { updateOrderStatus } = useOrderStore.getState();
      updateOrderStatus('1', 'completed');

      const state = useOrderStore.getState();
      expect(state.orders[0].status).toBe('completed');
      expect(state.orders[1].status).toBe('pending');
    });
  });

  describe('reset action', () => {
    it('clears all orders and stats', () => {
      const order: Order = {
        id: '1',
        customerName: 'Test',
        customerEmail: 'test@example.com',
        itemDescription: 'Service',
        quantity: 1,
        pricePerItem: 10,
        totalPrice: 10,
        status: 'pending',
        createdAt: '2024-03-01',
        updatedAt: '2024-03-01',
      };

      useOrderStore.setState({
        orders: [order],
        stats: computeStats([order]),
        error: 'Some error',
        isLoading: false,
      });

      const { reset } = useOrderStore.getState();
      reset();

      const state = useOrderStore.getState();
      expect(state.orders).toEqual([]);
      expect(state.stats).toEqual({
        totalOrders: 0,
        pendingOrders: 0,
        readyOrders: 0,
        completedOrders: 0,
        totalRevenue: 0,
      });
      expect(state.error).toBeNull();
      expect(state.isLoading).toBe(false);
    });
  });
});

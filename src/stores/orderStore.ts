import { create } from 'zustand';

export type OrderStatus = 'pending' | 'ready' | 'completed';

export interface Order {
  id: string;
  customerName: string;
  customerEmail: string;
  customerPhone?: string;
  itemDescription: string;
  quantity: number;
  pricePerItem: number;
  totalPrice: number;
  status: OrderStatus;
  createdAt: string;
  updatedAt: string;
  readyAt?: string;
}

export interface NewOrderPayload {
  customerName: string;
  customerEmail: string;
  customerPhone?: string;
  itemDescription: string;
  quantity: number;
  pricePerItem: number;
}

export interface OrderStats {
  totalOrders: number;
  pendingOrders: number;
  readyOrders: number;
  completedOrders: number;
  totalRevenue: number;
}

type OrderFetcher = () => Promise<Order[]>;
type OrderCreator = (payload: NewOrderPayload) => Promise<Order>;

interface OrderState {
  orders: Order[];
  stats: OrderStats;
  isLoading: boolean;
  error: string | null;
  fetchOrders: (fetcher?: OrderFetcher) => Promise<void>;
  addOrder: (payload: NewOrderPayload, creator?: OrderCreator) => Promise<void>;
  updateOrderStatus: (id: string, status: OrderStatus) => void;
  reset: () => void;
}

const now = () => new Date().toISOString();

const sampleOrders: Order[] = [
  {
    id: '100',
    customerName: 'Alice Johnson',
    customerEmail: 'alice@example.com',
    customerPhone: '123-456-7890',
    itemDescription: 'Wash & Fold',
    quantity: 3,
    pricePerItem: 12.5,
    totalPrice: 37.5,
    status: 'pending',
    createdAt: now(),
    updatedAt: now(),
  },
  {
    id: '101',
    customerName: 'Marco Liu',
    customerEmail: 'marco@example.com',
    itemDescription: 'Dry Cleaning',
    quantity: 2,
    pricePerItem: 18,
    totalPrice: 36,
    status: 'ready',
    createdAt: now(),
    updatedAt: now(),
    readyAt: now(),
  },
  {
    id: '102',
    customerName: 'Priya Kumar',
    customerEmail: 'priya@example.com',
    customerPhone: '555-0102',
    itemDescription: 'Alterations',
    quantity: 1,
    pricePerItem: 25,
    totalPrice: 25,
    status: 'completed',
    createdAt: now(),
    updatedAt: now(),
    readyAt: now(),
  },
];

const initialStats: OrderStats = {
  totalOrders: 0,
  pendingOrders: 0,
  readyOrders: 0,
  completedOrders: 0,
  totalRevenue: 0,
};

const initialState = {
  orders: [] as Order[],
  stats: initialStats,
  isLoading: false,
  error: null as string | null,
};

const computeStats = (orders: Order[]): OrderStats => {
  return orders.reduce<OrderStats>(
    (accumulator, order) => {
      const totals = {
        ...accumulator,
        totalOrders: accumulator.totalOrders + 1,
        totalRevenue: accumulator.totalRevenue + order.totalPrice,
      };

      if (order.status === 'pending') {
        return { ...totals, pendingOrders: totals.pendingOrders + 1 };
      }

      if (order.status === 'ready') {
        return { ...totals, readyOrders: totals.readyOrders + 1 };
      }

      if (order.status === 'completed') {
        return { ...totals, completedOrders: totals.completedOrders + 1 };
      }

      return totals;
    },
    { ...initialStats },
  );
};

export const orderApi = {
  async fetchOrders(): Promise<Order[]> {
    // In a real application, this would call the backend.
    // Here we just simulate a fast API response with mock data.
    await new Promise((resolve) => setTimeout(resolve, 25));
    return sampleOrders;
  },

  async createOrder(payload: NewOrderPayload): Promise<Order> {
    await new Promise((resolve) => setTimeout(resolve, 10));
    const id = Math.floor(Math.random() * 1_000_000).toString();
    const createdAt = now();
    return {
      id,
      createdAt,
      updatedAt: createdAt,
      totalPrice: payload.quantity * payload.pricePerItem,
      status: 'pending',
      ...payload,
    };
  },
};

export const useOrderStore = create<OrderState>((set, get) => ({
  ...initialState,
  fetchOrders: async (fetcher = orderApi.fetchOrders) => {
    set({ isLoading: true, error: null });

    try {
      const orders = await fetcher();
      set({
        orders,
        stats: computeStats(orders),
        isLoading: false,
      });
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Unable to load order data.';
      set({ error: message, isLoading: false });
    }
  },
  addOrder: async (payload, creator = orderApi.createOrder) => {
    set({ isLoading: true, error: null });

    try {
      const newOrder = await creator(payload);
      const orders = [...get().orders, newOrder];
      set({
        orders,
        stats: computeStats(orders),
        isLoading: false,
      });
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Unable to create a new order.';
      set({ error: message, isLoading: false });
    }
  },
  updateOrderStatus: (id, status) => {
    const orders = get().orders.map((order) =>
      order.id === id
        ? {
            ...order,
            status,
            readyAt: status === 'ready' || status === 'completed' ? now() : order.readyAt,
            updatedAt: now(),
          }
        : order,
    );

    set({
      orders,
      stats: computeStats(orders),
    });
  },
  reset: () => set({ ...initialState }),
}));

export const selectOrders = (state: OrderState) => state.orders;
export const selectStats = (state: OrderState) => state.stats;
export const selectLoadingState = (state: OrderState) => ({
  isLoading: state.isLoading,
  error: state.error,
});
export const selectError = (state: OrderState) => state.error;
export const selectIsLoading = (state: OrderState) => state.isLoading;

export const { reset: resetOrderStore } = useOrderStore.getState();

export { computeStats };

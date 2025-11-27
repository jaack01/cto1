import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DashboardStats } from '@/components/DashboardStats';
import { orderApi, resetOrderStore, type Order } from '@/stores/orderStore';

const buildOrder = (overrides: Partial<Order>): Order => ({
  id: 'order-id',
  customerName: 'Laundry Customer',
  customerEmail: 'customer@example.com',
  itemDescription: 'Wash & Fold',
  quantity: 1,
  pricePerItem: 10,
  totalPrice: 10,
  status: 'pending',
  createdAt: '2024-03-01T10:00:00.000Z',
  updatedAt: '2024-03-01T10:00:00.000Z',
  ...overrides,
});

describe('DashboardStats', () => {
  beforeEach(() => {
    resetOrderStore();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders a loading indicator while fetching data', () => {
    vi.spyOn(orderApi, 'fetchOrders').mockImplementation(() => new Promise(() => {}));

    render(<DashboardStats />);

    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
  });

  it('renders aggregated statistics for fetched orders', async () => {
    vi.spyOn(orderApi, 'fetchOrders').mockResolvedValue([
      buildOrder({ id: '1', status: 'pending', totalPrice: 32.5 }),
      buildOrder({ id: '2', status: 'ready', totalPrice: 18 }),
      buildOrder({ id: '3', status: 'completed', totalPrice: 45 }),
      buildOrder({ id: '4', status: 'ready', totalPrice: 12 }),
    ]);

    render(<DashboardStats />);

    expect(await screen.findByTestId('dashboard-stats')).toBeInTheDocument();

    expect(screen.getByTestId('total-orders')).toHaveTextContent('4');
    expect(screen.getByTestId('pending-orders')).toHaveTextContent('1');
    expect(screen.getByTestId('ready-orders')).toHaveTextContent('2');
    expect(screen.getByTestId('completed-orders')).toHaveTextContent('1');
    expect(screen.getByTestId('total-revenue')).toHaveTextContent('$107.50');

    expect(orderApi.fetchOrders).toHaveBeenCalledTimes(1);
  });

  it('renders an error message when fetching fails', async () => {
    vi.spyOn(orderApi, 'fetchOrders').mockRejectedValue(new Error('Network offline'));

    render(<DashboardStats />);

    expect(await screen.findByTestId('error-message')).toHaveTextContent('Network offline');
    expect(orderApi.fetchOrders).toHaveBeenCalledTimes(1);
  });

  it('renders zeroed metrics when no orders are returned', async () => {
    vi.spyOn(orderApi, 'fetchOrders').mockResolvedValue([]);

    render(<DashboardStats />);

    expect(await screen.findByTestId('dashboard-stats')).toBeInTheDocument();
    expect(screen.getByTestId('total-orders')).toHaveTextContent('0');
    expect(screen.getByTestId('pending-orders')).toHaveTextContent('0');
    expect(screen.getByTestId('ready-orders')).toHaveTextContent('0');
    expect(screen.getByTestId('completed-orders')).toHaveTextContent('0');
    expect(screen.getByTestId('total-revenue')).toHaveTextContent('$0.00');
  });
});

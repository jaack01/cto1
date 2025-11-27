import React, { useEffect, useRef } from 'react';
import { useOrderStore, selectStats } from '@/stores/orderStore';

export const DashboardStats: React.FC = () => {
  const stats = useOrderStore(selectStats);
  const isLoading = useOrderStore((state) => state.isLoading);
  const error = useOrderStore((state) => state.error);

  const hasCalledFetch = useRef(false);

  useEffect(() => {
    if (!hasCalledFetch.current) {
      hasCalledFetch.current = true;
      void useOrderStore.getState().fetchOrders();
    }
  }, []);

  if (isLoading) {
    return <div data-testid="loading-indicator">Loading...</div>;
  }

  if (error) {
    return <div data-testid="error-message">{error}</div>;
  }

  return (
    <div data-testid="dashboard-stats">
      <h2>Dashboard Statistics</h2>
      <div>
        <span>Total Orders: </span>
        <strong data-testid="total-orders">{stats.totalOrders}</strong>
      </div>
      <div>
        <span>Pending: </span>
        <strong data-testid="pending-orders">{stats.pendingOrders}</strong>
      </div>
      <div>
        <span>Ready: </span>
        <strong data-testid="ready-orders">{stats.readyOrders}</strong>
      </div>
      <div>
        <span>Completed: </span>
        <strong data-testid="completed-orders">{stats.completedOrders}</strong>
      </div>
      <div>
        <span>Total Revenue: </span>
        <strong data-testid="total-revenue">${stats.totalRevenue.toFixed(2)}</strong>
      </div>
    </div>
  );
};

export default DashboardStats;

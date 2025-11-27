import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { OrderForm } from '@/components/OrderForm';
import { orderApi, resetOrderStore } from '@/stores/orderStore';

describe('OrderForm', () => {
  beforeEach(() => {
    resetOrderStore();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders form fields with appropriate labels', () => {
    render(<OrderForm />);

    expect(screen.getByLabelText(/customer name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/customer email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/customer phone/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/service description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/quantity/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/price per item/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save order/i })).toBeInTheDocument();
  });

  it('displays validation errors for required fields', async () => {
    const user = userEvent.setup();
    render(<OrderForm />);

    const submitButton = screen.getByRole('button', { name: /save order/i });
    await user.click(submitButton);

    expect(await screen.findByTestId('error-customer-name')).toHaveTextContent(
      'Customer name is required',
    );
    expect(screen.getByTestId('error-customer-email')).toHaveTextContent(
      'Customer email is required',
    );
    expect(screen.getByTestId('error-item-description')).toHaveTextContent(
      'Item description is required',
    );
  });

  it('validates email format correctly', async () => {
    const user = userEvent.setup();
    render(<OrderForm />);

    const nameField = screen.getByLabelText(/customer name/i);
    await user.type(nameField, 'Test User');

    const emailField = screen.getByLabelText(/customer email/i);
    await user.type(emailField, 'not-a-valid-email');

    const itemField = screen.getByLabelText(/service description/i);
    await user.type(itemField, 'Test Service');

    const submitButton = screen.getByRole('button', { name: /save order/i });
    await user.click(submitButton);

    expect(await screen.findByTestId('error-customer-email')).toHaveTextContent(
      'Provide a valid email address',
    );
  });

  it('calculates and displays order total dynamically', async () => {
    const user = userEvent.setup();
    render(<OrderForm />);

    const quantityField = screen.getByLabelText(/quantity/i);
    const priceField = screen.getByLabelText(/price per item/i);

    await user.clear(quantityField);
    await user.type(quantityField, '3');

    await user.clear(priceField);
    await user.type(priceField, '15.50');

    expect(screen.getByTestId('order-total')).toHaveTextContent('$46.50');
  });

  it('submits valid form data and calls addOrder', async () => {
    const user = userEvent.setup();
    const mockCreateOrder = vi.spyOn(orderApi, 'createOrder').mockResolvedValue({
      id: '999',
      customerName: 'Jane Doe',
      customerEmail: 'jane@example.com',
      customerPhone: '555-1234',
      itemDescription: 'Express Laundry',
      quantity: 2,
      pricePerItem: 20,
      totalPrice: 40,
      status: 'pending',
      createdAt: '2024-03-01T10:00:00.000Z',
      updatedAt: '2024-03-01T10:00:00.000Z',
    });

    const mockOnSuccess = vi.fn();
    render(<OrderForm onSuccess={mockOnSuccess} />);

    await user.type(screen.getByLabelText(/customer name/i), 'Jane Doe');
    await user.type(screen.getByLabelText(/customer email/i), 'jane@example.com');
    await user.type(screen.getByLabelText(/customer phone/i), '555-1234');
    await user.type(screen.getByLabelText(/service description/i), 'Express Laundry');

    const quantityField = screen.getByLabelText(/quantity/i);
    await user.clear(quantityField);
    await user.type(quantityField, '2');

    const priceField = screen.getByLabelText(/price per item/i);
    await user.clear(priceField);
    await user.type(priceField, '20');

    const submitButton = screen.getByRole('button', { name: /save order/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockCreateOrder).toHaveBeenCalledWith({
        customerName: 'Jane Doe',
        customerEmail: 'jane@example.com',
        customerPhone: '555-1234',
        itemDescription: 'Express Laundry',
        quantity: 2,
        pricePerItem: 20,
      });
    });

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  it('clears field errors when user starts typing', async () => {
    const user = userEvent.setup();
    render(<OrderForm />);

    const submitButton = screen.getByRole('button', { name: /save order/i });
    await user.click(submitButton);

    expect(await screen.findByTestId('error-customer-name')).toBeInTheDocument();

    const nameField = screen.getByLabelText(/customer name/i);
    await user.type(nameField, 'J');

    expect(screen.queryByTestId('error-customer-name')).not.toBeInTheDocument();
  });

  it('disables submit button while loading', async () => {
    const user = userEvent.setup();
    vi.spyOn(orderApi, 'createOrder').mockImplementation(
      () => new Promise(() => {}),
    );

    render(<OrderForm />);

    await user.type(screen.getByLabelText(/customer name/i), 'Test User');
    await user.type(screen.getByLabelText(/customer email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/service description/i), 'Test Service');

    const submitButton = screen.getByRole('button', { name: /save order/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(submitButton).toBeDisabled();
      expect(submitButton).toHaveTextContent(/saving order/i);
    });
  });
});

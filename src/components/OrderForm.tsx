import React, { useState } from 'react';
import { useOrderStore } from '@/stores/orderStore';

interface FormState {
  customerName: string;
  customerEmail: string;
  customerPhone: string;
  itemDescription: string;
  quantity: number;
  pricePerItem: number;
}

interface OrderFormProps {
  onSuccess?: () => void;
}

const defaultFormState: FormState = {
  customerName: '',
  customerEmail: '',
  customerPhone: '',
  itemDescription: '',
  quantity: 1,
  pricePerItem: 0,
};

export const OrderForm: React.FC<OrderFormProps> = ({ onSuccess }) => {
  const addOrder = useOrderStore((state) => state.addOrder);
  const isLoading = useOrderStore((state) => state.isLoading);
  const storeError = useOrderStore((state) => state.error);

  const [formState, setFormState] = useState<FormState>(defaultFormState);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [submissionError, setSubmissionError] = useState<string | null>(null);

  const validate = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formState.customerName.trim()) {
      errors.customerName = 'Customer name is required';
    }

    if (!formState.customerEmail.trim()) {
      errors.customerEmail = 'Customer email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formState.customerEmail)) {
      errors.customerEmail = 'Provide a valid email address';
    }

    if (!formState.itemDescription.trim()) {
      errors.itemDescription = 'Item description is required';
    }

    if (!formState.quantity || formState.quantity < 1) {
      errors.quantity = 'Quantity must be at least 1';
    }

    if (formState.pricePerItem < 0) {
      errors.pricePerItem = 'Price must be zero or greater';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (field: keyof FormState, value: string | number) => {
    setFormState((prev) => ({ ...prev, [field]: value }));
    if (formErrors[field]) {
      setFormErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmissionError(null);

    if (!validate()) {
      return;
    }

    try {
      await addOrder({
        customerName: formState.customerName,
        customerEmail: formState.customerEmail,
        customerPhone: formState.customerPhone || undefined,
        itemDescription: formState.itemDescription,
        quantity: formState.quantity,
        pricePerItem: formState.pricePerItem,
      });
      setFormState(defaultFormState);
      onSuccess?.();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Unable to submit the new order.';
      setSubmissionError(message);
    }
  };

  return (
    <form aria-label="Laundry order form" onSubmit={handleSubmit} noValidate>
      <h2>Create a New Order</h2>

      <label htmlFor="customerName">Customer name</label>
      <input
        id="customerName"
        value={formState.customerName}
        onChange={(event) => handleChange('customerName', event.target.value)}
        aria-invalid={Boolean(formErrors.customerName)}
      />
      {formErrors.customerName && (
        <p role="alert" data-testid="error-customer-name">
          {formErrors.customerName}
        </p>
      )}

      <label htmlFor="customerEmail">Customer email</label>
      <input
        id="customerEmail"
        type="email"
        value={formState.customerEmail}
        onChange={(event) => handleChange('customerEmail', event.target.value)}
        aria-invalid={Boolean(formErrors.customerEmail)}
      />
      {formErrors.customerEmail && (
        <p role="alert" data-testid="error-customer-email">
          {formErrors.customerEmail}
        </p>
      )}

      <label htmlFor="customerPhone">Customer phone</label>
      <input
        id="customerPhone"
        value={formState.customerPhone}
        onChange={(event) => handleChange('customerPhone', event.target.value)}
      />

      <label htmlFor="itemDescription">Service description</label>
      <input
        id="itemDescription"
        value={formState.itemDescription}
        onChange={(event) => handleChange('itemDescription', event.target.value)}
        aria-invalid={Boolean(formErrors.itemDescription)}
      />
      {formErrors.itemDescription && (
        <p role="alert" data-testid="error-item-description">
          {formErrors.itemDescription}
        </p>
      )}

      <label htmlFor="quantity">Quantity</label>
      <input
        id="quantity"
        type="number"
        min={1}
        value={formState.quantity}
        onChange={(event) =>
          handleChange('quantity', Number.parseInt(event.target.value, 10) || 0)
        }
        aria-invalid={Boolean(formErrors.quantity)}
      />
      {formErrors.quantity && (
        <p role="alert" data-testid="error-quantity">
          {formErrors.quantity}
        </p>
      )}

      <label htmlFor="pricePerItem">Price per item</label>
      <input
        id="pricePerItem"
        type="number"
        min={0}
        step={0.01}
        value={formState.pricePerItem}
        onChange={(event) =>
          handleChange('pricePerItem', Number.parseFloat(event.target.value) || 0)
        }
        aria-invalid={Boolean(formErrors.pricePerItem)}
      />
      {formErrors.pricePerItem && (
        <p role="alert" data-testid="error-price-per-item">
          {formErrors.pricePerItem}
        </p>
      )}

      <p data-testid="order-total">
        Estimated total: ${(formState.pricePerItem * formState.quantity).toFixed(2)}
      </p>

      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Saving order…' : 'Save order'}
      </button>

      {submissionError && (
        <p role="alert" data-testid="submission-error">
          {submissionError}
        </p>
      )}

      {storeError && !submissionError && (
        <p role="alert" data-testid="store-error">
          {storeError}
        </p>
      )}
    </form>
  );
};

export default OrderForm;

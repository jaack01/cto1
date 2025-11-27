# Testing Documentation

This document describes the testing setup for the Laundry CRM application's React/Next.js frontend with Zustand state management.

## Overview

The testing infrastructure uses:
- **Vitest** as the test runner (fast, ESM-native alternative to Jest)
- **React Testing Library (RTL)** for component testing
- **@testing-library/user-event** for simulating user interactions
- **@testing-library/jest-dom** for additional DOM matchers
- **JSDOM** for DOM environment simulation
- **TypeScript** for type safety

## Running Tests

### All tests (CI mode)
```bash
npm test
```

### Watch mode (for development)
```bash
npm run test:watch
```

## Test Structure

```
tests/
├── components/
│   ├── DashboardStats.test.tsx    # Dashboard statistics component
│   └── OrderForm.test.tsx         # Order creation form
├── stores/
│   └── orderStore.test.ts         # Zustand store logic
└── setup.ts                        # Global test configuration
```

## Sample Test Coverage

### 1. Component Tests

#### DashboardStats (`tests/components/DashboardStats.test.tsx`)

Tests the dashboard statistics display component that fetches and renders order metrics:

- ✅ Renders loading indicator during data fetch
- ✅ Displays aggregated statistics (total orders, pending, ready, completed, revenue)
- ✅ Shows error messages on fetch failure
- ✅ Handles empty state (zero orders)

**Key patterns:**
- Mocking the `orderApi.fetchOrders` function
- Using `await screen.findByTestId()` for async updates
- Verifying proper data aggregation and formatting (e.g., currency display)

#### OrderForm (`tests/components/OrderForm.test.tsx`)

Tests the order creation form with validation and Zustand store integration:

- ✅ Renders all form fields with proper labels
- ✅ Validates required fields (name, email, description)
- ✅ Validates email format using regex
- ✅ Calculates order total dynamically (quantity × price)
- ✅ Submits valid data and calls the store's `addOrder` action
- ✅ Clears field errors when user corrects input
- ✅ Disables submit button during async submission

**Key patterns:**
- Using `userEvent.setup()` for realistic user interactions
- Mocking `orderApi.createOrder` to test submission flow
- Testing form validation without triggering HTML5 validation (`noValidate` attribute)
- Verifying callback invocation with `mockOnSuccess`

### 2. Store Tests

#### orderStore (`tests/stores/orderStore.test.ts`)

Tests the Zustand store's state management and async actions:

**`computeStats` utility:**
- ✅ Returns zeroed stats for empty order list
- ✅ Tallies orders by status (pending/ready/completed)
- ✅ Sums total revenue across all orders
- ✅ Handles multiple orders with same status

**`fetchOrders` action:**
- ✅ Sets loading state during fetch, then clears it
- ✅ Stores fetched orders and updates statistics
- ✅ Sets error message if fetcher throws
- ✅ Uses `orderApi.fetchOrders` by default

**`addOrder` action:**
- ✅ Creates new order and appends to orders list
- ✅ Updates statistics after adding
- ✅ Sets error if creator rejects
- ✅ Uses `orderApi.createOrder` by default

**`updateOrderStatus` action:**
- ✅ Updates status of target order by ID
- ✅ Sets `readyAt` timestamp when marking as 'ready'
- ✅ Leaves other orders unchanged
- ✅ Recomputes statistics

**`reset` action:**
- ✅ Clears all orders and resets stats to zero
- ✅ Clears error state

**Key patterns:**
- Direct store method invocation with `useOrderStore.getState()`
- Mocking API functions with `vi.spyOn()` and `.mockResolvedValue()`
- Testing loading states by checking `isLoading` mid-promise
- Using `resetOrderStore()` in `beforeEach` for test isolation

## Mocking Strategy

### API Layer

The store tests inject mock fetchers/creators to avoid actual API calls:

```typescript
const mockFetcher = vi.fn(async () => mockOrders);
await useOrderStore.getState().fetchOrders(mockFetcher);
```

For component tests, we spy on the `orderApi` methods:

```typescript
vi.spyOn(orderApi, 'fetchOrders').mockResolvedValue(sampleOrders);
```

### Store Isolation

Each test file calls `resetOrderStore()` in `beforeEach` to ensure a clean slate. This prevents state leakage between tests.

## Configuration Files

### vitest.config.ts

- Enables React plugin for JSX transformation
- Sets up jsdom environment for DOM APIs
- Configures path aliases (`@/*` → `src/*`)
- Loads global test setup from `tests/setup.ts`

### tsconfig.json

- Includes Vitest global types
- Enables `@testing-library/jest-dom` types
- Configures strict TypeScript checks

### tests/setup.ts

Imports `@testing-library/jest-dom` to provide custom matchers like:
- `toBeInTheDocument()`
- `toHaveTextContent()`
- `toBeDisabled()`

## Best Practices

1. **Use semantic queries**: Prefer `getByRole`, `getByLabelText` over `getByTestId`
2. **Wait for async updates**: Use `await screen.findBy*` or `waitFor(() => { ... })`
3. **Reset store state**: Always call `resetOrderStore()` in `beforeEach`
4. **Mock external dependencies**: Spy on API methods rather than letting real calls execute
5. **Test user behavior**: Simulate real interactions with `userEvent` instead of `fireEvent`
6. **Verify aria attributes**: Check `aria-invalid`, `aria-label` for accessibility

## Continuous Integration

The test suite runs in CI-friendly mode by default:
- No watch mode
- Exits with non-zero code on failure
- Outputs to stdout for logging

Example CI script:
```yaml
- run: npm ci
- run: npm test
```

## Troubleshooting

### Infinite loops / "Maximum update depth exceeded"

- **Cause**: Using unstable selector or dependency in `useEffect`
- **Fix**: Use `useRef` to track if effect has run, or call store method directly:
  ```tsx
  useEffect(() => {
    void useOrderStore.getState().fetchOrders();
  }, []);
  ```

### Tests timing out

- **Cause**: Waiting for element that never appears
- **Fix**: Verify mock data is correct, check for typos in test IDs/labels
- **Debug**: Use `screen.debug()` to print current DOM state

### Type errors in tests

- **Cause**: Missing types for Vitest globals
- **Fix**: Ensure `tsconfig.json` includes `"types": ["vitest/globals"]`

## Future Enhancements

Potential additions to the test suite:
- Integration tests with Playwright for end-to-end order flow
- Visual regression tests for UI components
- Performance benchmarks for store operations
- Code coverage reporting (already configured in `vitest.config.ts`)

---

**Status**: ✅ All tests passing (23 tests across 3 suites)

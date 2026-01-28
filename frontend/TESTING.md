# Frontend Testing Guide

## Overview

The frontend uses **Vitest** and **React Testing Library** for unit testing. All tests are located alongside their components with `.test.tsx` or `.test.ts` extensions.

## Running Tests

```bash
# Run all tests once
npm test

# Run tests in watch mode (recommended during development)
npm test -- --watch

# Run tests with UI
npm test:ui

# Run tests with coverage
npm test:coverage
```

## Test Structure

### Test Files

- `src/components/ui/*.test.tsx` - UI component tests
- `src/components/servers/*.test.tsx` - Server component tests
- `src/lib/*.test.ts` - Utility and API tests

### Current Test Coverage

✅ **68 tests passing** across 6 test files:

1. **`api.test.ts`** (4 tests)
   - APIErrorResponse class behavior
   - Error code and message handling
   - Optional details support

2. **`LoadingSpinner.test.tsx`** (5 tests)
   - Size variants (sm, md, lg)
   - Accessibility attributes
   - Custom className support

3. **`Badge.test.tsx`** (17 tests)
   - All badge types (verified, new, stable, pvp, pve, etc.)
   - Styling variants
   - Unknown badge type fallback

4. **`ErrorMessage.test.tsx`** (11 tests)
   - Error message rendering
   - APIErrorResponse code handling (UNAUTHORIZED, FORBIDDEN, NOT_FOUND, etc.)
   - Retry button functionality
   - Custom title support

5. **`ServerCard.test.tsx`** (18 tests)
   - Server information display
   - Badge rendering (verified, new, stable, game mode, ruleset)
   - Cluster name display
   - Favorite count formatting
   - Link navigation

6. **`ServerRow.test.tsx`** (13 tests)
   - Compact row layout
   - Status and badge display
   - Player count formatting
   - Favorite count display
   - Link navigation

## Writing New Tests

### Component Test Template

```tsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { YourComponent } from './YourComponent'

describe('YourComponent', () => {
    it('renders correctly', () => {
        render(<YourComponent prop="value" />)
        expect(screen.getByText('Expected Text')).toBeInTheDocument()
    })
})
```

### Testing with Router

For components using `Link` or `useNavigate`, wrap in `BrowserRouter`:

```tsx
import { BrowserRouter } from 'react-router-dom'

function ComponentWrapper({ children }: { children: React.ReactNode }) {
    return <BrowserRouter>{children}</BrowserRouter>
}

render(
    <ComponentWrapper>
        <YourComponent />
    </ComponentWrapper>
)
```

### Testing with React Query

For components using `useQuery` or `useMutation`, use `QueryClientProvider`:

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
})

function ComponentWrapper({ children }: { children: React.ReactNode }) {
    return (
        <QueryClientProvider client={queryClient}>
            {children}
        </QueryClientProvider>
    )
}
```

## Best Practices

1. **Test user behavior, not implementation details**
   - Use `getByRole`, `getByLabelText`, `getByText` instead of querying by class names
   - Test what users see and interact with

2. **Use descriptive test names**
   - `it('renders server name')` ✅
   - `it('test1')` ❌

3. **Keep tests isolated**
   - Each test should be independent
   - Use `beforeEach` for common setup if needed

4. **Test edge cases**
   - Null/undefined values
   - Empty arrays/strings
   - Error states

5. **Accessibility testing**
   - Verify ARIA labels
   - Check keyboard navigation
   - Ensure screen reader compatibility

## Future Test Additions

Consider adding tests for:

- `ServerFilters` component (filter state management)
- `ServerList` component (pagination, loading states)
- `DashboardPage` (CRUD operations)
- `useServers` hook (data fetching, pagination)
- `useMyServers` hook (owner server list)
- Form validation (LoginPage, SignUpPage, ServerForm)
- Error boundary behavior

## Configuration

- **Setup file**: `src/test/setup.ts`
- **Vitest config**: `vite.config.ts` (test section)
- **Test environment**: jsdom (browser-like environment)

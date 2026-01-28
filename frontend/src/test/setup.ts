/**
 * Test setup file.
 *
 * Configures testing environment with React Testing Library and jest-dom matchers.
 */

import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Cleanup after each test
afterEach(() => {
    cleanup()
})

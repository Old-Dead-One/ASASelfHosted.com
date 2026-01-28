/**
 * Tests for API client error handling.
 */

import { describe, it, expect } from 'vitest'
import { APIErrorResponse } from './api'

describe('APIErrorResponse', () => {
    it('creates error with code and message', () => {
        const error = new APIErrorResponse({
            code: 'TEST_ERROR',
            message: 'Test error message',
        })

        expect(error).toBeInstanceOf(Error)
        expect(error).toBeInstanceOf(APIErrorResponse)
        expect(error.code).toBe('TEST_ERROR')
        expect(error.message).toBe('Test error message')
        expect(error.name).toBe('APIErrorResponse')
    })

    it('includes optional details', () => {
        const error = new APIErrorResponse({
            code: 'VALIDATION_ERROR',
            message: 'Validation failed',
            details: {
                field: 'email',
                reason: 'Invalid format',
            },
        })

        expect(error.details).toEqual({
            field: 'email',
            reason: 'Invalid format',
        })
    })

    it('works without details', () => {
        const error = new APIErrorResponse({
            code: 'SIMPLE_ERROR',
            message: 'Simple error',
        })

        expect(error.details).toBeUndefined()
    })

    it('can be caught as Error', () => {
        const error = new APIErrorResponse({
            code: 'CATCHABLE',
            message: 'Can be caught',
        })

        try {
            throw error
        } catch (e) {
            expect(e).toBeInstanceOf(Error)
            expect(e).toBeInstanceOf(APIErrorResponse)
            if (e instanceof APIErrorResponse) {
                expect(e.code).toBe('CATCHABLE')
            }
        }
    })
})

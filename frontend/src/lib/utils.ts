/**
 * Utility functions.
 *
 * Common utilities used across the frontend.
 */

import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge Tailwind CSS classes.
 *
 * Used for conditional class names and component composition.
 */
export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
}

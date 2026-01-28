/**
 * Reusable Button component with Tek-powered styling.
 *
 * Variants: primary (Tek), secondary (outline), ghost, danger.
 * Sizes: sm, md, lg.
 */

import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

const base =
  'inline-flex items-center justify-center rounded-md font-medium transition focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0'

const variants = {
  primary: [
    'relative overflow-hidden bg-primary text-primary-foreground border border-ring/25 shadow-sm shadow-black/40',
    'hover:shadow-md hover:shadow-black/50 hover:-translate-y-[1px] hover:border-ring/40',
    'active:translate-y-0 active:shadow-sm',
  ].join(' '),
  secondary: [
    'border border-input bg-transparent text-foreground/90',
    'hover:bg-muted/30 hover:border-foreground/25',
    'active:bg-muted/20',
  ].join(' '),
  ghost: [
    'bg-transparent text-foreground/80',
    'hover:bg-muted/25',
  ].join(' '),
  danger: [
    'relative overflow-hidden bg-destructive text-destructive-foreground border border-destructive/30 shadow-sm shadow-black/40',
    'hover:shadow-md hover:shadow-black/50 hover:-translate-y-[1px] hover:border-destructive/50',
    'active:translate-y-0 active:shadow-sm',
  ].join(' '),
}

const sizes = {
  sm: 'h-8 px-3 text-sm',
  md: 'h-10 px-4 text-sm',
  lg: 'h-11 px-5 text-base',
}

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', type = 'button', className, children, disabled, ...props }, ref) => {
    const showSeam = variant === 'primary' || variant === 'danger'
    const seamOpacity = variant === 'danger' ? 'bg-ring/30' : 'bg-ring/60'

    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled}
        className={cn(base, variants[variant], sizes[size], className)}
        {...props}
      >
        {showSeam && (
          <span
            className={cn('absolute inset-x-0 top-0 h-px rounded-t-md pointer-events-none', seamOpacity)}
            aria-hidden
          />
        )}
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'

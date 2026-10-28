import type { ButtonHTMLAttributes } from 'react'

export type ButtonVariant = 'primary' | 'accent' | 'secondary'

export type ButtonSize = 'sm' | 'md' | 'lg'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  fullWidth?: boolean
}

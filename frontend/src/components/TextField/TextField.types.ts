import type { InputHTMLAttributes } from 'react'

export interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: string
}

import type { HTMLAttributes } from 'react'

export type TextSize = 'sm' | 'md' | 'lg'

export type TextTone = 'default' | 'muted' | 'inverse'

export interface TextProps extends HTMLAttributes<HTMLElement> {
  as?: 'p' | 'span' | 'strong' | 'small'
  size?: TextSize
  tone?: TextTone
}

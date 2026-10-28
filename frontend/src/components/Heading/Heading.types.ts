import type { HTMLAttributes } from 'react'

export type HeadingLevel = 1 | 2 | 3 | 4 | 5 | 6

export interface HeadingProps extends HTMLAttributes<HTMLHeadingElement> {
  level?: HeadingLevel
}

import styles from './Text.module.scss'
import type { TextProps, TextSize, TextTone } from './Text.types.ts'

const sizeClasses: Record<TextSize, string> = {
  sm: styles.textSm,
  md: styles.textMd,
  lg: styles.textLg,
}

const toneClasses: Record<TextTone, string> = {
  default: styles.textDefault,
  muted: styles.textMuted,
  inverse: styles.textInverse,
}

export function Text({
  as: Tag = 'p',
  size = 'md',
  tone = 'default',
  className,
  ...props
}: TextProps) {
  const classes = [styles.text, sizeClasses[size], toneClasses[tone], className]
    .filter(Boolean)
    .join(' ')

  return <Tag className={classes} {...props} />
}

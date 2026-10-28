import styles from './Button.module.scss'
import type { ButtonProps, ButtonSize, ButtonVariant } from './Button.types.ts'

const variantClasses: Record<ButtonVariant, string> = {
  primary: styles.buttonPrimary,
  accent: styles.buttonAccent,
  secondary: styles.buttonSecondary,
}

const sizeClasses: Record<ButtonSize, string> = {
  sm: styles.buttonSm,
  md: styles.buttonMd,
  lg: styles.buttonLg,
}

export function Button({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  type = 'button',
  className,
  ...props
}: ButtonProps) {
  const classes = [
    styles.button,
    variantClasses[variant],
    sizeClasses[size],
    fullWidth && styles.buttonFullWidth,
    className,
  ]
    .filter(Boolean)
    .join(' ')

  return <button type={type} className={classes} {...props} />
}

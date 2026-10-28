import { useId } from 'react'
import styles from './TextField.module.scss'
import type { TextFieldProps } from './TextField.types.ts'

export function TextField({ label, error, id, className, ...props }: TextFieldProps) {
  const generatedId = useId()
  const inputId = id ?? generatedId
  const errorId = `${inputId}-error`
  const classes = [styles.textFieldInput, error && styles.textFieldInputInvalid]
    .filter(Boolean)
    .join(' ')

  return (
    <div className={[styles.textField, className].filter(Boolean).join(' ')}>
      <label className={styles.textFieldLabel} htmlFor={inputId}>
        {label}
      </label>
      <input
        id={inputId}
        className={classes}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? errorId : undefined}
        {...props}
      />
      {error && (
        <span id={errorId} className={styles.textFieldError} role="alert">
          {error}
        </span>
      )}
    </div>
  )
}

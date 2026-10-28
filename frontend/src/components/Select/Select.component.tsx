import { useId } from 'react'
import styles from './Select.module.scss'
import type { SelectProps } from './Select.types.ts'

export function Select({ label, options, id, className, ...props }: SelectProps) {
  const generatedId = useId()
  const selectId = id ?? generatedId

  return (
    <div className={[styles.select, className].filter(Boolean).join(' ')}>
      <label className={styles.selectLabel} htmlFor={selectId}>
        {label}
      </label>
      <select id={selectId} className={styles.selectInput} {...props}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  )
}

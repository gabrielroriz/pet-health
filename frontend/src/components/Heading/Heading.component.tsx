import styles from './Heading.module.scss'
import type { HeadingProps } from './Heading.types.ts'

export function Heading({ level = 2, className, ...props }: HeadingProps) {
  const Tag = `h${level}` as const
  const classes = [styles.heading, styles[`headingLevel${level}`], className]
    .filter(Boolean)
    .join(' ')

  return <Tag className={classes} {...props} />
}

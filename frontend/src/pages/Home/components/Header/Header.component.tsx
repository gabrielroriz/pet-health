import { Button } from '../../../../components/Button/index.tsx'
import { Text } from '../../../../components/Text/index.tsx'
import styles from './Header.module.scss'
import type { HeaderProps } from './Header.types.ts'

export function Header({ email, onLogOut }: HeaderProps) {
  return (
    <header className={styles.header}>
      <div className={styles.headerBrand}>
        <img className={styles.headerLogo} src="/favicon.png" alt="" />
        <Text as="strong" size="lg" tone="inverse">
          Pet Health
        </Text>
      </div>
      <div className={styles.headerUser}>
        {email && (
          <Text as="span" size="sm" tone="inverse">
            {email}
          </Text>
        )}
        <Button variant="accent" size="sm" onClick={onLogOut}>
          Log out
        </Button>
      </div>
    </header>
  )
}

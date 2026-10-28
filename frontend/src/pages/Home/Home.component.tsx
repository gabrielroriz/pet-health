import { useAuth } from '../../modules/auth/context/AuthContext.ts'
import { useCurrentUser } from '../../modules/auth/hooks/useCurrentUser.ts'
import { Button } from '../../components/Button/index.tsx'
import { Heading } from '../../components/Heading/index.tsx'
import { Text } from '../../components/Text/index.tsx'
import styles from './Home.module.scss'

export function Home() {
  const { logOut } = useAuth()
  const { data: user, isError } = useCurrentUser()

  return (
    <main className={styles.home}>
      <Heading level={1}>Pet Health</Heading>
      {user && <Text>Logged in as {user.email}.</Text>}
      {isError && <Text tone="muted">Could not load your account.</Text>}
      <Button variant="secondary" onClick={logOut}>
        Log out
      </Button>
    </main>
  )
}

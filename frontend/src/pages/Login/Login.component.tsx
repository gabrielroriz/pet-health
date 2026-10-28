import { useState, type FormEvent } from 'react'
import { useLocation, useNavigate, type Location } from 'react-router'
import { useLogIn } from '../../modules/auth/hooks/useLogIn.ts'
import { Button } from '../../components/Button/index.tsx'
import { Heading } from '../../components/Heading/index.tsx'
import { Text } from '../../components/Text/index.tsx'
import { TextField } from '../../components/TextField/index.tsx'
import styles from './Login.module.scss'

export function Login() {
  const logIn = useLogIn()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    logIn.mutate(email, {
      onSuccess: () => {
        const from = (location.state as { from?: Location } | null)?.from?.pathname ?? '/'
        navigate(from, { replace: true })
      },
    })
  }

  return (
    <main className={styles.login}>
      <form className={styles.loginCard} onSubmit={handleSubmit}>
        <img className={styles.loginLogo} src="/favicon.png" alt="" />
        <Heading level={1} className={styles.loginTitle}>
          Pet Health
        </Heading>
        <Text tone="muted" className={styles.loginSubtitle}>Log in with your email.</Text>
        <TextField
          label="Email"
          type="email"
          name="email"
          autoComplete="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          error={logIn.error?.message}
        />
        <Button type="submit" variant="highlight" fullWidth disabled={logIn.isPending}>
          {logIn.isPending ? 'Logging in…' : 'Log in'}
        </Button>
      </form>
    </main>
  )
}

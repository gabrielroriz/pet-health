import { useQuery } from '@tanstack/react-query'
import { useEffect } from 'react'
import { useAuth } from '../context/AuthContext.ts'
import { fetchCurrentUser, UnauthorizedError } from '../api/authApi.ts'

export function useCurrentUser() {
  const { token, logOut } = useAuth()

  const query = useQuery({
    queryKey: ['auth', 'me', token],
    queryFn: () => fetchCurrentUser(token!),
    enabled: token !== null,
  })

  // The backend rejects the token (for example after it restarts): end the session.
  const unauthorized = query.error instanceof UnauthorizedError
  useEffect(() => {
    if (unauthorized) {
      logOut()
    }
  }, [unauthorized, logOut])

  return query
}

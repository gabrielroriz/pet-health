import { useQueryClient } from '@tanstack/react-query'
import { useCallback, useMemo, useState, type ReactNode } from 'react'
import { AuthContext } from './AuthContext.ts'

const TOKEN_KEY = 'pet-health.token'

function readStoredToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

// Holds the session token. Server data lives in the TanStack Query cache.
export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [token, setToken] = useState(readStoredToken)

  const saveToken = useCallback((newToken: string) => {
    localStorage.setItem(TOKEN_KEY, newToken)
    setToken(newToken)
  }, [])

  // Drops the cached data too, so the next user never sees the previous one's.
  const logOut = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    queryClient.clear()
  }, [queryClient])

  const value = useMemo(() => ({ token, saveToken, logOut }), [token, saveToken, logOut])

  return <AuthContext value={value}>{children}</AuthContext>
}

interface TokenResponse {
  access_token: string
  token_type: string
}

export interface CurrentUser {
  id: string
  email: string
}

export class UnauthorizedError extends Error {}

export async function requestToken(email: string): Promise<string> {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  })
  if (!response.ok) {
    throw new Error('Could not log in. Check your email and try again.')
  }
  const data: TokenResponse = await response.json()
  return data.access_token
}

export async function fetchCurrentUser(token: string): Promise<CurrentUser> {
  const response = await fetch('/api/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (response.status === 401) {
    throw new UnauthorizedError('Your session has expired.')
  }
  if (!response.ok) {
    throw new Error('Could not load your account.')
  }
  return response.json()
}

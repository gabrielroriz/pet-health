import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderToString } from 'react-dom/server'
import { MemoryRouter } from 'react-router'
import { describe, expect, test } from 'vitest'
import App from './App.tsx'
import { AuthContext } from '../modules/auth/context/AuthContext.ts'

function renderAt(path: string, token: string | null) {
  const auth = { token, saveToken: () => {}, logOut: () => {} }
  return renderToString(
    <QueryClientProvider client={new QueryClient()}>
      <AuthContext value={auth}>
        <MemoryRouter initialEntries={[path]}>
          <App />
        </MemoryRouter>
      </AuthContext>
    </QueryClientProvider>,
  )
}

describe('App routes', () => {
  test('shows the login page to guests', () => {
    expect(renderAt('/login', null)).toContain('Log in')
  })

  test('keeps guests out of private pages', () => {
    expect(renderAt('/', null)).not.toContain('Log out')
  })

  test('shows private pages to logged-in users', () => {
    expect(renderAt('/', 'token')).toContain('Log out')
  })

  test('keeps logged-in users out of the login page', () => {
    expect(renderAt('/login', 'token')).not.toContain('Log in with your email')
  })
})

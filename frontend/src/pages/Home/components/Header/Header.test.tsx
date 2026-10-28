import { renderToString } from 'react-dom/server'
import { describe, expect, test } from 'vitest'
import { Header } from './Header.component.tsx'

describe('Header', () => {
  test('shows the user email and a log out button', () => {
    const html = renderToString(<Header email="ana@example.com" onLogOut={() => {}} />)
    expect(html).toContain('ana@example.com')
    expect(html).toContain('Log out')
  })
})

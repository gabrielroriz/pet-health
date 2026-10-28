import { renderToString } from 'react-dom/server'
import { describe, expect, test } from 'vitest'
import { Text } from './Text.component.tsx'

describe('Text', () => {
  test('renders a medium, default-tone paragraph by default', () => {
    const html = renderToString(<Text>Healthy pets</Text>)
    expect(html).toMatch(/^<p[^>]*class="[^"]*textMd[^"]*textDefault/)
    expect(html).toContain('Healthy pets')
  })

  test('renders the requested element, size and tone', () => {
    const html = renderToString(
      <Text as="span" size="sm" tone="muted">
        Note
      </Text>,
    )
    expect(html).toMatch(/^<span[^>]*class="[^"]*textSm[^"]*textMuted/)
  })
})

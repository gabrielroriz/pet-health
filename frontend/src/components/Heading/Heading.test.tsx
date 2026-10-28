import { renderToString } from 'react-dom/server'
import { describe, expect, test } from 'vitest'
import { Heading } from './Heading.component.tsx'

describe('Heading', () => {
  test('renders an h2 by default', () => {
    const html = renderToString(<Heading>Our services</Heading>)
    expect(html).toMatch(/^<h2[^>]*>Our services<\/h2>$/)
  })

  test('renders the requested level', () => {
    const html = renderToString(<Heading level={1}>Welcome</Heading>)
    expect(html).toMatch(/^<h1[^>]*class="[^"]*headingLevel1/)
  })

  test('keeps a custom class name', () => {
    expect(renderToString(<Heading className="custom">Hi</Heading>)).toContain('custom')
  })
})

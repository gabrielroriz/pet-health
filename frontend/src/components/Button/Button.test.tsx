import { renderToString } from 'react-dom/server'
import { describe, expect, test } from 'vitest'
import { Button } from './Button.component.tsx'

describe('Button', () => {
  test('renders its children', () => {
    expect(renderToString(<Button>Book a visit</Button>)).toContain('Book a visit')
  })

  test('defaults to a primary, medium, non-submitting button', () => {
    const html = renderToString(<Button>Save</Button>)
    expect(html).toContain('type="button"')
    expect(html).toMatch(/class="[^"]*buttonPrimary[^"]*buttonMd/)
  })

  test('applies the variant, size and full-width classes', () => {
    const html = renderToString(
      <Button variant="accent" size="lg" fullWidth>
        Join
      </Button>,
    )
    expect(html).toMatch(/class="[^"]*buttonAccent[^"]*buttonLg[^"]*buttonFullWidth/)
  })

  test('forwards native attributes', () => {
    const html = renderToString(
      <Button type="submit" disabled>
        Send
      </Button>,
    )
    expect(html).toContain('type="submit"')
    expect(html).toContain('disabled')
  })
})

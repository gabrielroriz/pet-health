import { renderToString } from 'react-dom/server'
import { describe, expect, test } from 'vitest'
import { TextField } from './TextField.component.tsx'

describe('TextField', () => {
  test('links the label to the input', () => {
    const html = renderToString(<TextField id="email" label="Email" />)
    expect(html).toContain('for="email"')
    expect(html).toContain('id="email"')
    expect(html).toContain('Email')
  })

  test('shows the error and marks the input invalid', () => {
    const html = renderToString(<TextField id="email" label="Email" error="Required" />)
    expect(html).toContain('aria-invalid="true"')
    expect(html).toContain('aria-describedby="email-error"')
    expect(html).toMatch(/class="[^"]*textFieldInputInvalid/)
    expect(html).toContain('Required')
  })

  test('forwards native attributes', () => {
    const html = renderToString(<TextField label="Email" type="email" required />)
    expect(html).toContain('type="email"')
    expect(html).toContain('required')
  })
})

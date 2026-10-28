import { renderToString } from 'react-dom/server'
import { describe, expect, test } from 'vitest'
import { Select } from './Select.component.tsx'

const options = [
  { value: '15', label: '15 minutes' },
  { value: '30', label: '30 minutes' },
]

describe('Select', () => {
  test('links the label to the select', () => {
    const html = renderToString(<Select id="duration" label="Duration" options={options} />)
    expect(html).toContain('for="duration"')
    expect(html).toContain('<select id="duration"')
  })

  test('renders the options and the selected value', () => {
    const html = renderToString(
      <Select label="Duration" options={options} value="30" onChange={() => {}} />,
    )
    expect(html).toContain('15 minutes')
    expect(html).toMatch(/<option value="30" selected="">30 minutes/)
  })
})

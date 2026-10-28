import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderToString } from 'react-dom/server'
import { describe, expect, test } from 'vitest'
import { ScheduleAppointmentForm } from './ScheduleAppointmentForm.component.tsx'

describe('ScheduleAppointmentForm', () => {
  test('asks for the pet, date, duration and reason', () => {
    const html = renderToString(
      <QueryClientProvider client={new QueryClient()}>
        <ScheduleAppointmentForm />
      </QueryClientProvider>,
    )
    expect(html).toContain('Pet name')
    expect(html).toContain('type="datetime-local"')
    expect(html).toContain('Duration')
    expect(html).toMatch(/<option value="30" selected="">/)
    expect(html).toContain('Reason')
    expect(html).toContain('type="submit"')
  })
})

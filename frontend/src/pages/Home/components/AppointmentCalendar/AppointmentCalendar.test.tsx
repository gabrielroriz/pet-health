import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderToString } from 'react-dom/server'
import { describe, expect, test } from 'vitest'
import { appointmentsQueryKey } from '../../../../modules/appointments/hooks/useAppointments.ts'
import { AppointmentCalendar } from './AppointmentCalendar.component.tsx'
import { dayKey, groupByDay, monthGrid } from './AppointmentCalendar.utils.ts'

const thor = {
  id: '1',
  petName: 'Thor',
  scheduledAt: new Date(2026, 10, 2, 10, 0).toISOString(),
  durationMinutes: 30,
  reason: 'Vaccines',
}

describe('monthGrid', () => {
  test('covers the month in whole weeks starting on Sunday', () => {
    const weeks = monthGrid(new Date(2026, 9, 15))
    expect(dayKey(weeks[0][0])).toBe('2026-09-27')
    expect(dayKey(weeks.at(-1)!.at(-1)!)).toBe('2026-10-31')
    expect(weeks.every((week) => week.length === 7)).toBe(true)
  })

  test('pads the last week with days from the next month', () => {
    const weeks = monthGrid(new Date(2026, 10, 1))
    expect(dayKey(weeks[0][0])).toBe('2026-11-01')
    expect(dayKey(weeks.at(-1)!.at(-1)!)).toBe('2026-12-05')
  })

  test('adds no extra week when the month fits exactly', () => {
    expect(monthGrid(new Date(2026, 1, 1))).toHaveLength(4)
  })
})

describe('groupByDay', () => {
  test('groups appointments by their local day', () => {
    expect(groupByDay([thor]).get('2026-11-02')).toEqual([thor])
  })
})

describe('AppointmentCalendar', () => {
  test('shows the month and its appointments', () => {
    const queryClient = new QueryClient()
    queryClient.setQueryData(appointmentsQueryKey, [thor])
    const html = renderToString(
      <QueryClientProvider client={queryClient}>
        <AppointmentCalendar initialMonth={new Date(2026, 10, 20)} />
      </QueryClientProvider>,
    )
    expect(html).toContain('dateTime="2026-11"')
    expect(html).toContain('Thor')
    expect(html).toContain('Previous month')
  })
})

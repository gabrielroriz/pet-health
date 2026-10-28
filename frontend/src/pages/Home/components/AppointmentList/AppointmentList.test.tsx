import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderToString } from 'react-dom/server'
import { describe, expect, test } from 'vitest'
import type { Appointment } from '../../../../modules/appointments/api/appointmentApi.ts'
import { appointmentsQueryKey } from '../../../../modules/appointments/hooks/useAppointments.ts'
import { AppointmentList } from './AppointmentList.component.tsx'

function renderWith(appointments?: Appointment[]) {
  const queryClient = new QueryClient()
  if (appointments) {
    queryClient.setQueryData(appointmentsQueryKey, appointments)
  }
  return renderToString(
    <QueryClientProvider client={queryClient}>
      <AppointmentList />
    </QueryClientProvider>,
  )
}

describe('AppointmentList', () => {
  test('shows a loading message before the data arrives', () => {
    expect(renderWith()).toContain('Loading appointments')
  })

  test('shows an empty state', () => {
    expect(renderWith([])).toContain('No appointments yet')
  })

  test('lists the appointments', () => {
    const html = renderWith([
      { id: '1', petName: 'Thor', scheduledAt: '2026-11-02T13:00:00.000Z', durationMinutes: 30, reason: 'Vaccines' },
      { id: '2', petName: 'Luna', scheduledAt: '2026-11-03T13:00:00.000Z', durationMinutes: 30, reason: 'Check-up' },
    ])
    expect(html).toContain('Thor')
    expect(html).toContain('Luna')
  })
})

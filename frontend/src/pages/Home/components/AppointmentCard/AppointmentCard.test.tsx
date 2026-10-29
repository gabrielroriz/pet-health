import { renderToString } from 'react-dom/server'
import { describe, expect, test } from 'vitest'
import type { Appointment } from '../../../../modules/appointments/api/appointmentApi.ts'
import { AppointmentCard } from './AppointmentCard.component.tsx'

const appointment: Appointment = {
  id: '1',
  petId: 'p1',
  hospitalId: 'h1',
  veterinarianId: 'v1',
  startsAt: '2026-11-02T13:00:00.000Z',
  endsAt: '2026-11-02T13:30:00.000Z',
  durationMinutes: 30,
  reason: 'Annual vaccines',
  status: 'scheduled',
}

const labels = {
  petName: 'Thor',
  veterinarianName: 'Dr. Beatriz Costa',
  hospitalName: 'PetCare Downtown',
}

describe('AppointmentCard', () => {
  test('shows the pet, reason, duration, veterinarian, hospital and date', () => {
    const html = renderToString(
      <AppointmentCard appointment={appointment} labels={labels} onCancel={() => {}} />,
    )
    expect(html).toContain('Thor')
    expect(html).toContain('Annual vaccines')
    expect(html).toContain('30 min')
    expect(html).toContain('Dr. Beatriz Costa · PetCare Downtown')
    expect(html).toContain('dateTime="2026-11-02T13:00:00.000Z"')
  })

  test('disables the cancel button while cancelling', () => {
    const html = renderToString(
      <AppointmentCard appointment={appointment} labels={labels} onCancel={() => {}} cancelling />,
    )
    expect(html).toContain('Cancelling…')
    expect(html).toContain('disabled')
  })
})

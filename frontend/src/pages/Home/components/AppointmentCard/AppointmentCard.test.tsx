import { renderToString } from 'react-dom/server'
import { describe, expect, test } from 'vitest'
import { AppointmentCard } from './AppointmentCard.component.tsx'

const appointment = {
  id: '1',
  petName: 'Thor',
  scheduledAt: '2026-11-02T13:00:00.000Z',
  durationMinutes: 30,
  reason: 'Annual vaccines',
}

describe('AppointmentCard', () => {
  test('shows the pet, reason, date and duration', () => {
    const html = renderToString(<AppointmentCard appointment={appointment} onCancel={() => {}} />)
    expect(html).toContain('Thor')
    expect(html).toContain('Annual vaccines')
    expect(html).toContain('30 min')
    expect(html).toContain('dateTime="2026-11-02T13:00:00.000Z"')
  })

  test('disables the cancel button while cancelling', () => {
    const html = renderToString(
      <AppointmentCard appointment={appointment} onCancel={() => {}} cancelling />,
    )
    expect(html).toContain('Cancelling…')
    expect(html).toContain('disabled')
  })
})

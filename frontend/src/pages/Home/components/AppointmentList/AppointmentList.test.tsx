import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderToString } from 'react-dom/server'
import { describe, expect, test } from 'vitest'
import type { Appointment } from '../../../../modules/appointments/api/appointmentApi.ts'
import { appointmentsQueryKey } from '../../../../modules/appointments/hooks/useAppointments.ts'
import { AuthContext } from '../../../../modules/auth/context/AuthContext.ts'
import { hospitalsQueryKey } from '../../../../modules/hospitals/hooks/useHospitals.ts'
import { petsQueryKey } from '../../../../modules/pets/hooks/usePets.ts'
import { veterinariansQueryKey } from '../../../../modules/veterinarians/hooks/useVeterinarians.ts'
import { AppointmentList } from './AppointmentList.component.tsx'

const auth = { token: 'token', saveToken: () => {}, logOut: () => {} }

function appointment(id: string, petId: string, startsAt: string): Appointment {
  return {
    id,
    petId,
    hospitalId: 'h1',
    veterinarianId: 'v1',
    startsAt,
    endsAt: startsAt,
    durationMinutes: 30,
    reason: 'Check-up',
    status: 'scheduled',
  }
}

function renderWith(appointments?: Appointment[], { withNames = true } = {}) {
  const queryClient = new QueryClient()
  if (appointments) {
    queryClient.setQueryData(appointmentsQueryKey, appointments)
  }
  if (withNames) {
    queryClient.setQueryData(petsQueryKey, [
      { id: 'p1', name: 'Thor' },
      { id: 'p2', name: 'Luna' },
    ])
    queryClient.setQueryData(veterinariansQueryKey, [{ id: 'v1', name: 'Dr. Beatriz Costa' }])
    queryClient.setQueryData(hospitalsQueryKey, [{ id: 'h1', name: 'PetCare Downtown' }])
  }
  return renderToString(
    <QueryClientProvider client={queryClient}>
      <AuthContext value={auth}>
        <AppointmentList />
      </AuthContext>
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

  test('lists the appointments with the names of their pet, veterinarian and hospital', () => {
    const html = renderWith([
      appointment('1', 'p1', '2026-11-02T13:00:00.000Z'),
      appointment('2', 'p2', '2026-11-03T13:00:00.000Z'),
    ])
    expect(html).toContain('Thor')
    expect(html).toContain('Luna')
    expect(html).toContain('Dr. Beatriz Costa · PetCare Downtown')
  })

  test('shows a placeholder until the names arrive', () => {
    const html = renderWith([appointment('1', 'p1', '2026-11-02T13:00:00.000Z')], { withNames: false })
    expect(html).toContain('… · …')
  })
})

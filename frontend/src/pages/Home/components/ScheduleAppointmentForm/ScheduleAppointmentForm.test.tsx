import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderToString } from 'react-dom/server'
import { describe, expect, test } from 'vitest'
import { AuthContext } from '../../../../modules/auth/context/AuthContext.ts'
import { hospitalsQueryKey } from '../../../../modules/hospitals/hooks/useHospitals.ts'
import { petsQueryKey } from '../../../../modules/pets/hooks/usePets.ts'
import { ScheduleAppointmentForm } from './ScheduleAppointmentForm.component.tsx'

const auth = { token: 'token', saveToken: () => {}, logOut: () => {} }

const hospitals = [
  { id: 'h1', name: 'Happy Paws Clinic', network: null },
  { id: 'h2', name: 'PetCare Downtown', network: { id: 'n1', name: 'PetCare Network' } },
]

function renderWith(pets: { id: string; name: string }[]) {
  const queryClient = new QueryClient()
  queryClient.setQueryData(petsQueryKey, pets)
  queryClient.setQueryData(hospitalsQueryKey, hospitals)
  return renderToString(
    <QueryClientProvider client={queryClient}>
      <AuthContext value={auth}>
        <ScheduleAppointmentForm />
      </AuthContext>
    </QueryClientProvider>,
  )
}

describe('ScheduleAppointmentForm', () => {
  test('asks for the pet, hospital, time, duration, veterinarian and reason', () => {
    const html = renderWith([{ id: 'p1', name: 'Thor' }])

    expect(html).toContain('Choose a pet')
    expect(html).toContain('<option value="p1">Thor</option>')
    expect(html).toContain('Happy Paws Clinic')
    expect(html).toContain('PetCare Downtown (PetCare Network)')
    expect(html).toContain('type="datetime-local"')
    expect(html).toMatch(/<option value="30" selected="">/)
    expect(html).toContain('Reason')
    expect(html).toContain('type="submit"')
  })

  test('waits for a hospital and a time before listing veterinarians', () => {
    const html = renderWith([{ id: 'p1', name: 'Thor' }])

    expect(html).toMatch(/<select(?=[^>]*name="veterinarianId")(?=[^>]*disabled="")[^>]*>/)
    expect(html).toContain('Choose a hospital and a time first')
  })

  test('tells users without pets', () => {
    expect(renderWith([])).toContain('No pets yet')
  })
})

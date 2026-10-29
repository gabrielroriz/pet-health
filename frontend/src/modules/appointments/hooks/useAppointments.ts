import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../../auth/context/AuthContext.ts'
import { listAppointments } from '../api/appointmentApi.ts'

export const appointmentsQueryKey = ['appointments']

export function useAppointments() {
  const { token } = useAuth()

  return useQuery({
    queryKey: appointmentsQueryKey,
    queryFn: () => listAppointments(token!),
    enabled: token !== null,
  })
}

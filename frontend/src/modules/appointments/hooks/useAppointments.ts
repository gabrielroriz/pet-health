import { useQuery } from '@tanstack/react-query'
import { listAppointments } from '../api/appointmentApi.ts'

export const appointmentsQueryKey = ['appointments']

export function useAppointments() {
  return useQuery({
    queryKey: appointmentsQueryKey,
    queryFn: listAppointments,
  })
}

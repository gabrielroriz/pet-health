import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '../../auth/context/AuthContext.ts'
import { availableVeterinariansQueryKey } from '../../veterinarians/hooks/useAvailableVeterinarians.ts'
import { scheduleAppointment, type NewAppointment } from '../api/appointmentApi.ts'
import { appointmentsQueryKey } from './useAppointments.ts'

export function useScheduleAppointment() {
  const { token } = useAuth()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (input: NewAppointment) => scheduleAppointment(token!, input),
    // Booked or turned down (409), the agenda may have changed: refresh the list and availability.
    onSettled: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: appointmentsQueryKey }),
        queryClient.invalidateQueries({ queryKey: availableVeterinariansQueryKey }),
      ]),
  })
}

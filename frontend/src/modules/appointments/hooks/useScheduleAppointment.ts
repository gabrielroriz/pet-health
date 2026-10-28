import { useMutation, useQueryClient } from '@tanstack/react-query'
import { scheduleAppointment } from '../api/appointmentApi.ts'
import { appointmentsQueryKey } from './useAppointments.ts'

export function useScheduleAppointment() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: scheduleAppointment,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: appointmentsQueryKey }),
  })
}

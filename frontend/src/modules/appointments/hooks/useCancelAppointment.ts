import { useMutation, useQueryClient } from '@tanstack/react-query'
import { cancelAppointment } from '../api/appointmentApi.ts'
import { appointmentsQueryKey } from './useAppointments.ts'

export function useCancelAppointment() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: cancelAppointment,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: appointmentsQueryKey }),
  })
}

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '../../auth/context/AuthContext.ts'
import { availableVeterinariansQueryKey } from '../../veterinarians/hooks/useAvailableVeterinarians.ts'
import { cancelAppointment } from '../api/appointmentApi.ts'
import { appointmentsQueryKey } from './useAppointments.ts'

export function useCancelAppointment() {
  const { token } = useAuth()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => cancelAppointment(token!, id),
    // The cancelled time is free again: refresh the list and availability.
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: appointmentsQueryKey }),
        queryClient.invalidateQueries({ queryKey: availableVeterinariansQueryKey }),
      ]),
  })
}

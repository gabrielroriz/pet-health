import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../../auth/context/AuthContext.ts'
import { listAvailableVeterinarians, type AvailabilityQuery } from '../api/veterinarianApi.ts'

// Prefix of every availability query, to refresh them all after a booking changes.
export const availableVeterinariansQueryKey = ['veterinarians', 'available']

// Fetches only once the slot is complete; pass null while it isn't.
export function useAvailableVeterinarians(slot: AvailabilityQuery | null) {
  const { token } = useAuth()

  return useQuery({
    queryKey: [...availableVeterinariansQueryKey, slot],
    queryFn: () => listAvailableVeterinarians(token!, slot!),
    enabled: token !== null && slot !== null,
  })
}

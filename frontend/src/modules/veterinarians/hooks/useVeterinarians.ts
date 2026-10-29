import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../../auth/context/AuthContext.ts'
import { listVeterinarians } from '../api/veterinarianApi.ts'

export const veterinariansQueryKey = ['veterinarians']

export function useVeterinarians() {
  const { token } = useAuth()

  return useQuery({
    queryKey: veterinariansQueryKey,
    queryFn: () => listVeterinarians(token!),
    enabled: token !== null,
  })
}

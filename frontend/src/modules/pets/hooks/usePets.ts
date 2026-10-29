import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../../auth/context/AuthContext.ts'
import { listPets } from '../api/petApi.ts'

export const petsQueryKey = ['pets']

export function usePets() {
  const { token } = useAuth()

  return useQuery({
    queryKey: petsQueryKey,
    queryFn: () => listPets(token!),
    enabled: token !== null,
  })
}

import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../../auth/context/AuthContext.ts'
import { listHospitals } from '../api/hospitalApi.ts'

export const hospitalsQueryKey = ['hospitals']

export function useHospitals() {
  const { token } = useAuth()

  return useQuery({
    queryKey: hospitalsQueryKey,
    queryFn: () => listHospitals(token!),
    enabled: token !== null,
  })
}

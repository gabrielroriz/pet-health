import { useMutation } from '@tanstack/react-query'
import { useAuth } from '../context/AuthContext.ts'
import { requestToken } from '../api/authApi.ts'

export function useLogIn() {
  const { saveToken } = useAuth()

  return useMutation({
    mutationFn: requestToken,
    onSuccess: saveToken,
  })
}

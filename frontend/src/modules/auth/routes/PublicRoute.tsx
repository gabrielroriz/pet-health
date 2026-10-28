import { Navigate, Outlet } from 'react-router'
import { useAuth } from '../context/AuthContext.ts'

// Renders its child routes only for guests; logged-in users go to the home page.
export function PublicRoute() {
  const { token } = useAuth()

  if (token) {
    return <Navigate to="/" replace />
  }
  return <Outlet />
}

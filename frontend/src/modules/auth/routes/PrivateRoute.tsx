import { Navigate, Outlet, useLocation } from 'react-router'
import { useAuth } from '../context/AuthContext.ts'

// Renders its child routes only for logged-in users; others go to the login page.
export function PrivateRoute() {
  const { token } = useAuth()
  const location = useLocation()

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }
  return <Outlet />
}

import { Navigate, Route, Routes } from 'react-router'
import { Home } from '../pages/Home/index.tsx'
import { Login } from '../pages/Login/index.tsx'
import { PrivateRoute } from '../modules/auth/routes/PrivateRoute.tsx'
import { PublicRoute } from '../modules/auth/routes/PublicRoute.tsx'

function App() {
  return (
    <Routes>
      <Route element={<PublicRoute />}>
        <Route path="/login" element={<Login />} />
      </Route>
      <Route element={<PrivateRoute />}>
        <Route path="/" element={<Home />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App

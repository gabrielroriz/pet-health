import { apiRequest } from '../../auth/api/apiClient.ts'

export interface HospitalNetwork {
  id: string
  name: string
}

export interface Hospital {
  id: string
  name: string
  // null for an independent hospital.
  network: HospitalNetwork | null
}

// Hospitals sorted by name, each with its network.
export async function listHospitals(token: string): Promise<Hospital[]> {
  return apiRequest<Hospital[]>('/hospitals', token)
}

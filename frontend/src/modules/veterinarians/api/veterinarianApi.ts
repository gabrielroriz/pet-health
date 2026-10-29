import { apiRequest } from '../../auth/api/apiClient.ts'

export interface Veterinarian {
  id: string
  name: string
  hospitalIds: string[]
}

// The time slot to check: a hospital, a start (ISO 8601 with timezone) and a length.
export interface AvailabilityQuery {
  hospitalId: string
  startsAt: string
  durationMinutes: number
}

interface VeterinarianResponse {
  id: string
  name: string
  hospital_ids: string[]
}

function toVeterinarian(response: VeterinarianResponse): Veterinarian {
  return { id: response.id, name: response.name, hospitalIds: response.hospital_ids }
}

// Every veterinarian, with the hospitals they work at.
export async function listVeterinarians(token: string): Promise<Veterinarian[]> {
  const veterinarians = await apiRequest<VeterinarianResponse[]>('/veterinarians', token)
  return veterinarians.map(toVeterinarian)
}

// Veterinarians of the hospital with no appointment, at any hospital, during the slot.
export async function listAvailableVeterinarians(
  token: string,
  { hospitalId, startsAt, durationMinutes }: AvailabilityQuery,
): Promise<Veterinarian[]> {
  const params = new URLSearchParams({
    hospital_id: hospitalId,
    starts_at: startsAt,
    duration_minutes: String(durationMinutes),
  })
  const veterinarians = await apiRequest<VeterinarianResponse[]>(
    `/veterinarians/available?${params}`,
    token,
  )
  return veterinarians.map(toVeterinarian)
}

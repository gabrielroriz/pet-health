import { apiRequest } from '../../auth/api/apiClient.ts'

export type AppointmentStatus = 'scheduled' | 'cancelled'

export interface Appointment {
  id: string
  petId: string
  hospitalId: string
  veterinarianId: string
  startsAt: string
  endsAt: string
  durationMinutes: number
  reason: string
  status: AppointmentStatus
}

export type NewAppointment = Pick<
  Appointment,
  'petId' | 'hospitalId' | 'veterinarianId' | 'startsAt' | 'durationMinutes' | 'reason'
>

// The backend speaks snake_case; the app uses camelCase.
interface AppointmentResponse {
  id: string
  pet_id: string
  hospital_id: string
  veterinarian_id: string
  starts_at: string
  ends_at: string
  duration_minutes: number
  reason: string
  status: AppointmentStatus
}

function toAppointment(response: AppointmentResponse): Appointment {
  return {
    id: response.id,
    petId: response.pet_id,
    hospitalId: response.hospital_id,
    veterinarianId: response.veterinarian_id,
    startsAt: response.starts_at,
    endsAt: response.ends_at,
    durationMinutes: response.duration_minutes,
    reason: response.reason,
    status: response.status,
  }
}

// Scheduled appointments of the logged-in user, earliest first.
export async function listAppointments(token: string): Promise<Appointment[]> {
  const appointments = await apiRequest<AppointmentResponse[]>('/appointments', token)
  return appointments.map(toAppointment)
}

// The backend rejects overlaps for the same veterinarian or pet with a 409 and a message to show.
export async function scheduleAppointment(token: string, input: NewAppointment): Promise<Appointment> {
  const appointment = await apiRequest<AppointmentResponse>('/appointments', token, {
    method: 'POST',
    body: {
      pet_id: input.petId,
      hospital_id: input.hospitalId,
      veterinarian_id: input.veterinarianId,
      starts_at: input.startsAt,
      duration_minutes: input.durationMinutes,
      reason: input.reason,
    },
  })
  return toAppointment(appointment)
}

// Cancelling keeps the appointment as history and frees its time.
export async function cancelAppointment(token: string, id: string): Promise<void> {
  await apiRequest(`/appointments/${id}/cancel`, token, { method: 'POST' })
}

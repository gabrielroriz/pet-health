import type { Appointment } from '../../../../modules/appointments/api/appointmentApi.ts'

export interface AppointmentCardProps {
  appointment: Appointment
  onCancel: (id: string) => void
  cancelling?: boolean
}

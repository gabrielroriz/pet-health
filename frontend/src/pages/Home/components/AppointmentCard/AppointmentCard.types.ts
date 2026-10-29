import type { Appointment } from '../../../../modules/appointments/api/appointmentApi.ts'
import type { AppointmentLabels } from '../../../../modules/appointments/hooks/useAppointmentLabels.ts'

export interface AppointmentCardProps {
  appointment: Appointment
  // Names of the pet, veterinarian and hospital, which the appointment holds only as ids.
  labels: AppointmentLabels
  onCancel: (id: string) => void
  cancelling?: boolean
}

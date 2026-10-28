import { Text } from '../../../../components/Text/index.tsx'
import { useAppointments } from '../../../../modules/appointments/hooks/useAppointments.ts'
import { useCancelAppointment } from '../../../../modules/appointments/hooks/useCancelAppointment.ts'
import { AppointmentCard } from '../AppointmentCard/index.tsx'
import styles from './AppointmentList.module.scss'

export function AppointmentList() {
  const { data: appointments, isPending, isError } = useAppointments()
  const cancel = useCancelAppointment()

  if (isPending) {
    return <Text tone="muted">Loading appointments…</Text>
  }
  if (isError) {
    return <Text tone="muted">Could not load your appointments.</Text>
  }
  if (appointments.length === 0) {
    return <Text tone="muted">No appointments yet. Schedule one to get started.</Text>
  }

  return (
    <ul className={styles.appointmentList}>
      {appointments.map((appointment) => (
        <li key={appointment.id}>
          <AppointmentCard
            appointment={appointment}
            onCancel={cancel.mutate}
            cancelling={cancel.isPending && cancel.variables === appointment.id}
          />
        </li>
      ))}
    </ul>
  )
}

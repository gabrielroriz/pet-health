import { endOf } from '../../../../modules/appointments/api/appointmentApi.ts'
import { Button } from '../../../../components/Button/index.tsx'
import { Heading } from '../../../../components/Heading/index.tsx'
import { Text } from '../../../../components/Text/index.tsx'
import styles from './AppointmentCard.module.scss'
import type { AppointmentCardProps } from './AppointmentCard.types.ts'

const dateFormat = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' })

export function AppointmentCard({ appointment, onCancel, cancelling = false }: AppointmentCardProps) {
  return (
    <article className={styles.appointmentCard}>
      <div className={styles.appointmentCardDetails}>
        <Text as="span" size="sm" className={styles.appointmentCardDate}>
          <time dateTime={appointment.scheduledAt}>
            {dateFormat.formatRange(new Date(appointment.scheduledAt), endOf(appointment))}
          </time>
        </Text>
        <Heading level={3} className={styles.appointmentCardPet}>
          {appointment.petName}
        </Heading>
        <Text tone="muted">
          {`${appointment.reason} · ${appointment.durationMinutes} min`}
        </Text>
      </div>
      <Button
        variant="secondary"
        size="sm"
        disabled={cancelling}
        onClick={() => onCancel(appointment.id)}
      >
        {cancelling ? 'Cancelling…' : 'Cancel'}
      </Button>
    </article>
  )
}

import { useState, type FormEvent } from 'react'
import { Button } from '../../../../components/Button/index.tsx'
import { Select } from '../../../../components/Select/index.tsx'
import { TextField } from '../../../../components/TextField/index.tsx'
import { useScheduleAppointment } from '../../../../modules/appointments/hooks/useScheduleAppointment.ts'
import styles from './ScheduleAppointmentForm.module.scss'

const DURATION_OPTIONS = [15, 30, 45, 60].map((minutes) => ({
  value: String(minutes),
  label: `${minutes} minutes`,
}))

const DEFAULT_DURATION = '30'

export function ScheduleAppointmentForm() {
  const schedule = useScheduleAppointment()
  const [petName, setPetName] = useState('')
  const [scheduledAt, setScheduledAt] = useState('')
  const [duration, setDuration] = useState(DEFAULT_DURATION)
  const [reason, setReason] = useState('')

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    schedule.mutate(
      {
        petName,
        scheduledAt: new Date(scheduledAt).toISOString(),
        durationMinutes: Number(duration),
        reason,
      },
      {
        onSuccess: () => {
          setPetName('')
          setScheduledAt('')
          setDuration(DEFAULT_DURATION)
          setReason('')
        },
      },
    )
  }

  return (
    <form className={styles.scheduleAppointmentForm} onSubmit={handleSubmit}>
      <TextField
        label="Pet name"
        name="petName"
        required
        value={petName}
        onChange={(event) => setPetName(event.target.value)}
      />
      <TextField
        label="Date and time"
        type="datetime-local"
        name="scheduledAt"
        required
        value={scheduledAt}
        onChange={(event) => {
          setScheduledAt(event.target.value)
          schedule.reset()
        }}
        error={schedule.error?.message}
      />
      <Select
        label="Duration"
        name="durationMinutes"
        options={DURATION_OPTIONS}
        value={duration}
        onChange={(event) => {
          setDuration(event.target.value)
          schedule.reset()
        }}
      />
      <TextField
        label="Reason"
        name="reason"
        required
        value={reason}
        onChange={(event) => setReason(event.target.value)}
      />
      <Button type="submit" variant="highlight" fullWidth disabled={schedule.isPending}>
        {schedule.isPending ? 'Scheduling…' : 'Schedule appointment'}
      </Button>
    </form>
  )
}

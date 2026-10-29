import { useState, type FormEvent } from 'react'
import { Button } from '../../../../components/Button/index.tsx'
import { Select } from '../../../../components/Select/index.tsx'
import { TextField } from '../../../../components/TextField/index.tsx'
import { useScheduleAppointment } from '../../../../modules/appointments/hooks/useScheduleAppointment.ts'
import { useHospitals } from '../../../../modules/hospitals/hooks/useHospitals.ts'
import { usePets } from '../../../../modules/pets/hooks/usePets.ts'
import { useAvailableVeterinarians } from '../../../../modules/veterinarians/hooks/useAvailableVeterinarians.ts'
import styles from './ScheduleAppointmentForm.module.scss'

const DURATION_OPTIONS = [15, 30, 45, 60].map((minutes) => ({
  value: String(minutes),
  label: `${minutes} minutes`,
}))

const DEFAULT_DURATION = '30'

// datetime-local gives local time without a zone; the backend needs ISO 8601 with one.
function toIsoString(localDateTime: string): string | null {
  const date = new Date(localDateTime)
  return Number.isNaN(date.getTime()) ? null : date.toISOString()
}

interface OptionsQuery {
  isPending: boolean
  isError: boolean
  data?: unknown[]
}

// First option of a select: what to do, or why there is nothing to pick yet.
function placeholder(query: OptionsQuery, prompt: string, empty: string): string {
  if (query.isPending) {
    return 'Loading…'
  }
  if (query.isError) {
    return 'Could not load the options'
  }
  return query.data?.length ? prompt : empty
}

export function ScheduleAppointmentForm() {
  const schedule = useScheduleAppointment()
  const pets = usePets()
  const hospitals = useHospitals()
  const [petId, setPetId] = useState('')
  const [hospitalId, setHospitalId] = useState('')
  const [scheduledAt, setScheduledAt] = useState('')
  const [duration, setDuration] = useState(DEFAULT_DURATION)
  const [veterinarianId, setVeterinarianId] = useState('')
  const [reason, setReason] = useState('')

  // Once the hospital and the time are chosen, ask the backend who is free in that slot.
  const startsAt = toIsoString(scheduledAt)
  const slot = hospitalId && startsAt ? { hospitalId, startsAt, durationMinutes: Number(duration) } : null
  const veterinarians = useAvailableVeterinarians(slot)
  // After a refresh (say, a 409 because someone else booked them) the chosen one may be gone.
  const chosenVeterinarianId = veterinarians.data?.some((vet) => vet.id === veterinarianId)
    ? veterinarianId
    : ''

  // A veterinarian free in one slot may be busy in another, so changing the slot clears the choice.
  function resetVeterinarian() {
    setVeterinarianId('')
    schedule.reset()
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!startsAt || !chosenVeterinarianId) {
      return
    }
    schedule.mutate(
      {
        petId,
        hospitalId,
        veterinarianId: chosenVeterinarianId,
        startsAt,
        durationMinutes: Number(duration),
        reason,
      },
      {
        onSuccess: () => {
          setPetId('')
          setHospitalId('')
          setScheduledAt('')
          setDuration(DEFAULT_DURATION)
          setVeterinarianId('')
          setReason('')
        },
      },
    )
  }

  const petOptions = [
    { value: '', label: placeholder(pets, 'Choose a pet', 'No pets yet') },
    ...(pets.data ?? []).map((pet) => ({ value: pet.id, label: pet.name })),
  ]
  const hospitalOptions = [
    { value: '', label: placeholder(hospitals, 'Choose a hospital', 'No hospitals available') },
    ...(hospitals.data ?? []).map((hospital) => ({
      value: hospital.id,
      label: hospital.network ? `${hospital.name} (${hospital.network.name})` : hospital.name,
    })),
  ]
  const veterinarianOptions = [
    {
      value: '',
      label: slot
        ? placeholder(veterinarians, 'Choose a veterinarian', 'No veterinarian is free at this time')
        : 'Choose a hospital and a time first',
    },
    ...(veterinarians.data ?? []).map((veterinarian) => ({
      value: veterinarian.id,
      label: veterinarian.name,
    })),
  ]

  return (
    <form className={styles.scheduleAppointmentForm} onSubmit={handleSubmit}>
      <Select
        label="Pet"
        name="petId"
        required
        options={petOptions}
        value={petId}
        onChange={(event) => {
          setPetId(event.target.value)
          schedule.reset()
        }}
      />
      <Select
        label="Hospital"
        name="hospitalId"
        required
        options={hospitalOptions}
        value={hospitalId}
        onChange={(event) => {
          setHospitalId(event.target.value)
          resetVeterinarian()
        }}
      />
      <TextField
        label="Date and time"
        type="datetime-local"
        name="scheduledAt"
        required
        value={scheduledAt}
        onChange={(event) => {
          setScheduledAt(event.target.value)
          resetVeterinarian()
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
          resetVeterinarian()
        }}
      />
      <Select
        label="Veterinarian"
        name="veterinarianId"
        required
        disabled={!slot}
        options={veterinarianOptions}
        value={chosenVeterinarianId}
        onChange={(event) => {
          setVeterinarianId(event.target.value)
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

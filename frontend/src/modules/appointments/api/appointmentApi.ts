export interface Appointment {
  id: string
  petName: string
  scheduledAt: string
  durationMinutes: number
  reason: string
}

export type NewAppointment = Omit<Appointment, 'id'>

export class DoubleBookingError extends Error {}

// Mock data until the backend exposes appointment endpoints. Replace these
// bodies with fetch calls; the hooks that use them won't need to change.
function daysFromNow(days: number, hour: number): string {
  const date = new Date()
  date.setDate(date.getDate() + days)
  date.setHours(hour, 0, 0, 0)
  return date.toISOString()
}

let appointments: Appointment[] = [
  {
    id: '1',
    petName: 'Thor',
    scheduledAt: daysFromNow(1, 10),
    durationMinutes: 30,
    reason: 'Annual vaccines',
  },
  {
    id: '2',
    petName: 'Luna',
    scheduledAt: daysFromNow(5, 15),
    durationMinutes: 45,
    reason: 'Skin allergy follow-up',
  },
]

export function endOf(appointment: Pick<Appointment, 'scheduledAt' | 'durationMinutes'>): Date {
  return new Date(Date.parse(appointment.scheduledAt) + appointment.durationMinutes * 60_000)
}

// Back-to-back appointments are allowed: one may start exactly when another ends.
function overlaps(a: NewAppointment, b: NewAppointment): boolean {
  return Date.parse(a.scheduledAt) < endOf(b).getTime() && Date.parse(b.scheduledAt) < endOf(a).getTime()
}

export async function listAppointments(): Promise<Appointment[]> {
  return [...appointments].sort((a, b) => a.scheduledAt.localeCompare(b.scheduledAt))
}

export async function scheduleAppointment(input: NewAppointment): Promise<Appointment> {
  if (appointments.some((existing) => overlaps(input, existing))) {
    throw new DoubleBookingError('This time overlaps another appointment. Choose another time.')
  }
  const appointment = { id: crypto.randomUUID(), ...input }
  appointments = [...appointments, appointment]
  return appointment
}

export async function cancelAppointment(id: string): Promise<void> {
  appointments = appointments.filter((appointment) => appointment.id !== id)
}

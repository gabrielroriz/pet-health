import type { Appointment } from '../../../../modules/appointments/api/appointmentApi.ts'

// Local calendar day, so appointments land on the day the user sees.
export function dayKey(date: Date): string {
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${date.getFullYear()}-${month}-${day}`
}

// Weeks (Sunday to Saturday) covering the whole month, padded with days
// from the neighbouring months.
export function monthGrid(month: Date): Date[][] {
  const first = new Date(month.getFullYear(), month.getMonth(), 1)
  const cursor = new Date(first)
  cursor.setDate(1 - first.getDay())

  const weeks: Date[][] = []
  do {
    const week: Date[] = []
    for (let day = 0; day < 7; day++) {
      week.push(new Date(cursor))
      cursor.setDate(cursor.getDate() + 1)
    }
    weeks.push(week)
  } while (cursor.getMonth() === first.getMonth())
  return weeks
}

export function groupByDay(appointments: Appointment[]): Map<string, Appointment[]> {
  const groups = new Map<string, Appointment[]>()
  for (const appointment of appointments) {
    const key = dayKey(new Date(appointment.startsAt))
    groups.set(key, [...(groups.get(key) ?? []), appointment])
  }
  return groups
}

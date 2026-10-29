import { useState } from 'react'
import { Button } from '../../../../components/Button/index.tsx'
import { Text } from '../../../../components/Text/index.tsx'
import { useAppointmentLabels } from '../../../../modules/appointments/hooks/useAppointmentLabels.ts'
import { useAppointments } from '../../../../modules/appointments/hooks/useAppointments.ts'
import styles from './AppointmentCalendar.module.scss'
import type { AppointmentCalendarProps } from './AppointmentCalendar.types.ts'
import { dayKey, groupByDay, monthGrid } from './AppointmentCalendar.utils.ts'

const monthFormat = new Intl.DateTimeFormat(undefined, { month: 'long', year: 'numeric' })
const weekdayFormat = new Intl.DateTimeFormat(undefined, { weekday: 'short' })
const timeFormat = new Intl.DateTimeFormat(undefined, { timeStyle: 'short' })

function startOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), 1)
}

export function AppointmentCalendar({ initialMonth }: AppointmentCalendarProps) {
  const { data: appointments, isPending, isError } = useAppointments()
  const labelsFor = useAppointmentLabels()
  const [today] = useState(() => dayKey(new Date()))
  const [month, setMonth] = useState(() => startOfMonth(initialMonth ?? new Date()))

  if (isPending) {
    return <Text tone="muted">Loading appointments…</Text>
  }
  if (isError) {
    return <Text tone="muted">Could not load your appointments.</Text>
  }

  const weeks = monthGrid(month)
  const appointmentsByDay = groupByDay(appointments)
  const monthKey = dayKey(month).slice(0, 7)

  function moveMonth(offset: number) {
    setMonth((current) => new Date(current.getFullYear(), current.getMonth() + offset, 1))
  }

  return (
    <div className={styles.appointmentCalendar}>
      <div className={styles.appointmentCalendarToolbar}>
        <Text as="strong" size="lg" className={styles.appointmentCalendarMonth}>
          <time dateTime={monthKey}>{monthFormat.format(month)}</time>
        </Text>
        <div className={styles.appointmentCalendarNav}>
          <Button variant="secondary" size="sm" aria-label="Previous month" onClick={() => moveMonth(-1)}>
            ‹
          </Button>
          <Button variant="secondary" size="sm" onClick={() => setMonth(startOfMonth(new Date()))}>
            Today
          </Button>
          <Button variant="secondary" size="sm" aria-label="Next month" onClick={() => moveMonth(1)}>
            ›
          </Button>
        </div>
      </div>

      <div className={styles.appointmentCalendarGrid} role="grid" aria-label={monthFormat.format(month)}>
        <div className={styles.appointmentCalendarRow} role="row">
          {weeks[0].map((day) => (
            <div key={day.getDay()} className={styles.appointmentCalendarWeekday} role="columnheader">
              {weekdayFormat.format(day)}
            </div>
          ))}
        </div>
        {weeks.map((week) => (
          <div key={dayKey(week[0])} className={styles.appointmentCalendarRow} role="row">
            {week.map((day) => {
              const key = dayKey(day)
              const dayAppointments = appointmentsByDay.get(key) ?? []
              const classes = [
                styles.appointmentCalendarDay,
                day.getMonth() !== month.getMonth() && styles.appointmentCalendarDayOutside,
              ]
                .filter(Boolean)
                .join(' ')

              return (
                <div key={key} className={classes} role="gridcell">
                  <time
                    dateTime={key}
                    className={styles.appointmentCalendarDate}
                    aria-current={key === today ? 'date' : undefined}
                  >
                    {day.getDate()}
                  </time>
                  {dayAppointments.length > 0 && (
                    <ul className={styles.appointmentCalendarEvents}>
                      {dayAppointments.map((appointment) => {
                        const labels = labelsFor(appointment)
                        return (
                          <li
                            key={appointment.id}
                            className={styles.appointmentCalendarEvent}
                            title={`${labels.petName} · ${appointment.reason} · ${labels.veterinarianName}, ${labels.hospitalName}`}
                          >
                            <span className={styles.appointmentCalendarEventPet}>
                              {labels.petName}
                            </span>
                            <time
                              dateTime={appointment.startsAt}
                              className={styles.appointmentCalendarEventTime}
                            >
                              {timeFormat.format(new Date(appointment.startsAt))}
                            </time>
                          </li>
                        )
                      })}
                    </ul>
                  )}
                </div>
              )
            })}
          </div>
        ))}
      </div>
    </div>
  )
}

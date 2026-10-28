import { describe, expect, test } from 'vitest'
import { cancelAppointment, DoubleBookingError, scheduleAppointment } from './appointmentApi.ts'

function at(time: string, durationMinutes = 30) {
  return { petName: 'Thor', scheduledAt: `2030-01-01T${time}:00.000Z`, durationMinutes, reason: 'Check-up' }
}

describe('scheduleAppointment', () => {
  test('rejects an appointment that overlaps another one', async () => {
    const booked = await scheduleAppointment(at('10:00'))

    await expect(scheduleAppointment(at('10:15'))).rejects.toThrow(DoubleBookingError)
    await expect(scheduleAppointment(at('09:45'))).rejects.toThrow(DoubleBookingError)
    await expect(scheduleAppointment(at('09:00', 120))).rejects.toThrow(DoubleBookingError)

    await cancelAppointment(booked.id)
  })

  test('accepts back-to-back appointments', async () => {
    const first = await scheduleAppointment(at('14:00'))
    const before = await scheduleAppointment(at('13:30'))
    const after = await scheduleAppointment(at('14:30'))

    expect(after.scheduledAt).toBe('2030-01-01T14:30:00.000Z')

    await Promise.all([first, before, after].map((appointment) => cancelAppointment(appointment.id)))
  })

  test('frees the slot when an appointment is cancelled', async () => {
    const booked = await scheduleAppointment(at('16:00'))
    await cancelAppointment(booked.id)

    const rebooked = await scheduleAppointment(at('16:00'))
    expect(rebooked.id).not.toBe(booked.id)

    await cancelAppointment(rebooked.id)
  })
})

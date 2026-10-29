import { afterEach, describe, expect, test, vi } from 'vitest'
import { ApiError } from '../../auth/api/apiClient.ts'
import { cancelAppointment, listAppointments, scheduleAppointment } from './appointmentApi.ts'

const response = {
  id: 'a1',
  owner_id: 'u1',
  pet_id: 'p1',
  hospital_id: 'h1',
  veterinarian_id: 'v1',
  starts_at: '2030-01-01T10:00:00Z',
  ends_at: '2030-01-01T10:30:00Z',
  duration_minutes: 30,
  reason: 'Annual vaccines',
  status: 'scheduled',
}

const appointment = {
  id: 'a1',
  petId: 'p1',
  hospitalId: 'h1',
  veterinarianId: 'v1',
  startsAt: '2030-01-01T10:00:00Z',
  endsAt: '2030-01-01T10:30:00Z',
  durationMinutes: 30,
  reason: 'Annual vaccines',
  status: 'scheduled',
}

function respondWith(status: number, body: unknown) {
  const fetchMock = vi.fn(async (_url: string, _init?: RequestInit) => Response.json(body, { status }))
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('listAppointments', () => {
  test('converts the backend fields to camelCase', async () => {
    respondWith(200, [response])

    await expect(listAppointments('token')).resolves.toEqual([appointment])
  })
})

describe('scheduleAppointment', () => {
  test('posts the appointment in snake_case', async () => {
    const fetchMock = respondWith(201, response)

    const scheduled = await scheduleAppointment('token', {
      petId: 'p1',
      hospitalId: 'h1',
      veterinarianId: 'v1',
      startsAt: '2030-01-01T10:00:00Z',
      durationMinutes: 30,
      reason: 'Annual vaccines',
    })

    expect(scheduled).toEqual(appointment)
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/appointments')
    expect(init?.method).toBe('POST')
    expect(JSON.parse(String(init?.body))).toEqual({
      pet_id: 'p1',
      hospital_id: 'h1',
      veterinarian_id: 'v1',
      starts_at: '2030-01-01T10:00:00Z',
      duration_minutes: 30,
      reason: 'Annual vaccines',
    })
  })

  test('passes on why the backend refused a double booking', async () => {
    const detail = 'The veterinarian already has an appointment at this time. Choose another time.'
    respondWith(409, { detail })

    const booking = scheduleAppointment('token', {
      petId: 'p2',
      hospitalId: 'h1',
      veterinarianId: 'v1',
      startsAt: '2030-01-01T10:15:00Z',
      durationMinutes: 30,
      reason: 'Check-up',
    })

    await expect(booking).rejects.toBeInstanceOf(ApiError)
    await expect(booking).rejects.toThrow(detail)
  })
})

describe('cancelAppointment', () => {
  test('posts to the cancel endpoint of the appointment', async () => {
    const fetchMock = respondWith(200, { ...response, status: 'cancelled' })

    await cancelAppointment('token', 'a1')

    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/appointments/a1/cancel')
    expect(init?.method).toBe('POST')
  })
})

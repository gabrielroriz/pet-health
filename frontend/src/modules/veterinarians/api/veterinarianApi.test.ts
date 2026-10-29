import { afterEach, describe, expect, test, vi } from 'vitest'
import { listAvailableVeterinarians } from './veterinarianApi.ts'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('listAvailableVeterinarians', () => {
  test('asks for the slot in the query string and converts the result', async () => {
    const fetchMock = vi.fn(async (_url: string, _init?: RequestInit) =>
      Response.json([{ id: 'v1', name: 'Dr. Beatriz Costa', hospital_ids: ['h1', 'h2'] }]),
    )
    vi.stubGlobal('fetch', fetchMock)

    const veterinarians = await listAvailableVeterinarians('token', {
      hospitalId: 'h1',
      startsAt: '2030-01-01T10:00:00.000Z',
      durationMinutes: 45,
    })

    expect(veterinarians).toEqual([{ id: 'v1', name: 'Dr. Beatriz Costa', hospitalIds: ['h1', 'h2'] }])
    const url = new URL(fetchMock.mock.calls[0][0], 'http://localhost')
    expect(url.pathname).toBe('/api/veterinarians/available')
    expect(Object.fromEntries(url.searchParams)).toEqual({
      hospital_id: 'h1',
      starts_at: '2030-01-01T10:00:00.000Z',
      duration_minutes: '45',
    })
  })
})

import { afterEach, describe, expect, test, vi } from 'vitest'
import { ApiError, apiRequest } from './apiClient.ts'
import { UnauthorizedError } from './authApi.ts'

function respondWith(status: number, body: unknown) {
  const fetchMock = vi.fn(async (_url: string, _init?: RequestInit) => Response.json(body, { status }))
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('apiRequest', () => {
  test('calls the backend through the /api proxy with the bearer token', async () => {
    const fetchMock = respondWith(200, [{ id: '1' }])

    await expect(apiRequest('/pets', 'token-123')).resolves.toEqual([{ id: '1' }])
    expect(fetchMock).toHaveBeenCalledWith('/api/pets', {
      method: 'GET',
      headers: { Authorization: 'Bearer token-123' },
      body: undefined,
    })
  })

  test('sends the body as JSON', async () => {
    const fetchMock = respondWith(201, {})

    await apiRequest('/appointments', 'token-123', { method: 'POST', body: { reason: 'Vaccines' } })

    expect(fetchMock).toHaveBeenCalledWith('/api/appointments', {
      method: 'POST',
      headers: { Authorization: 'Bearer token-123', 'Content-Type': 'application/json' },
      body: '{"reason":"Vaccines"}',
    })
  })

  test('ends the session when the token is rejected', async () => {
    respondWith(401, { detail: 'Invalid or expired token.' })

    await expect(apiRequest('/pets', 'old-token')).rejects.toThrow(UnauthorizedError)
  })

  test('surfaces the message of a business rule', async () => {
    respondWith(409, { detail: 'The veterinarian already has an appointment at this time.' })

    const error = await apiRequest('/appointments', 'token').catch((caught: unknown) => caught)

    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({
      status: 409,
      message: 'The veterinarian already has an appointment at this time.',
    })
  })

  test('falls back to a generic message for malformed input', async () => {
    respondWith(422, { detail: [{ loc: ['body', 'reason'], msg: 'Field required' }] })

    await expect(apiRequest('/appointments', 'token')).rejects.toThrow('Something went wrong. Try again.')
  })
})

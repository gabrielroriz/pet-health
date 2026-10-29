import { UnauthorizedError } from './authApi.ts'

// An error response from the backend, with the message to show the user.
export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

const FALLBACK_MESSAGE = 'Something went wrong. Try again.'

interface RequestOptions {
  method?: 'GET' | 'POST'
  body?: unknown
}

// Calls the backend as the logged-in user and returns the parsed JSON body.
export async function apiRequest<T>(
  path: string,
  token: string,
  { method = 'GET', body }: RequestOptions = {},
): Promise<T> {
  const headers: Record<string, string> = { Authorization: `Bearer ${token}` }
  if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }
  const response = await fetch(`/api${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  if (response.status === 401) {
    throw new UnauthorizedError('Your session has expired.')
  }
  if (!response.ok) {
    throw new ApiError(response.status, await readDetail(response))
  }
  return response.json()
}

// FastAPI explains errors in "detail": a sentence for business rules, a list for malformed input.
async function readDetail(response: Response): Promise<string> {
  try {
    const { detail } = await response.json()
    return typeof detail === 'string' ? detail : FALLBACK_MESSAGE
  } catch {
    return FALLBACK_MESSAGE
  }
}

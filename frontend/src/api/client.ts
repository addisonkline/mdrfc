const TOKEN_KEY = 'mdrfc_token';

type QueryParamValue = string | number | boolean | null | undefined;

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearStoredToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

async function parseErrorDetail(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body?.detail === 'string') {
      return body.detail;
    }
  } catch {
    // Ignore JSON parse failures and fall back to the generic message below.
  }

  return `Request failed with status ${response.status}`;
}

export function buildApiPath<T extends object>(
  path: string,
  query: T = {} as T,
): string {
  const params = new URLSearchParams();

  for (const [key, value] of Object.entries(query) as Array<[string, QueryParamValue]>) {
    if (value === null || value === undefined) continue;
    params.set(key, String(value));
  }

  const queryString = params.toString();
  if (queryString.length === 0) {
    return path;
  }
  return `${path}?${queryString}`;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);

  const token = getStoredToken();
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  if (options.body && typeof options.body === 'string' && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`/api${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const detail = await parseErrorDetail(response);

    if (response.status === 401 && detail === 'could not validate credentials') {
      clearStoredToken();
    }

    throw new ApiError(response.status, detail);
  }

  return response.json();
}

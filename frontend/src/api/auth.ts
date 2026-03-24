import { ApiError, apiFetch } from './client';
import type { Token, SignupData, PostSignupResponse, PostVerifyEmailResponse } from '../types';

export async function login(username: string, password: string): Promise<Token> {
  const body = new URLSearchParams({ username, password });
  const response = await fetch('/api/login', {
    method: 'POST',
    body,
  });

  if (!response.ok) {
    let detail = 'Login failed';
    try {
      const data = await response.json();
      if (data.detail) detail = data.detail;
    } catch {
      // ignore
    }
    throw new ApiError(response.status, detail);
  }

  return response.json();
}

export async function signup(data: SignupData): Promise<PostSignupResponse> {
  return apiFetch<PostSignupResponse>('/signup', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function verifyEmail(token: string): Promise<PostVerifyEmailResponse> {
  return apiFetch<PostVerifyEmailResponse>('/verify-email', {
    method: 'POST',
    body: JSON.stringify({ token }),
  });
}

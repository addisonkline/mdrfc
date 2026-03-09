import { apiFetch } from './client';
import type { User } from '../types';

export async function getMe(): Promise<User> {
  return apiFetch<User>('/users/me');
}

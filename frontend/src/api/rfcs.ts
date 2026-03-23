import { apiFetch, buildApiPath } from './client';
import type {
  GetRfcsResponse,
  GetRfcResponse,
  PostRfcResponse,
  PatchRfcResponse,
  CreateRfcData,
  UpdateRfcData,
  GetRfcsQuery,
} from '../types';

export async function listRfcs(query: GetRfcsQuery = {}): Promise<GetRfcsResponse> {
  return apiFetch<GetRfcsResponse>(buildApiPath('/rfcs', query));
}

export async function getRfc(id: number): Promise<GetRfcResponse> {
  return apiFetch<GetRfcResponse>(`/rfcs/${id}`);
}

export async function createRfc(data: CreateRfcData): Promise<PostRfcResponse> {
  return apiFetch<PostRfcResponse>('/rfcs', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateRfc(id: number, data: UpdateRfcData): Promise<PatchRfcResponse> {
  return apiFetch<PatchRfcResponse>(`/rfcs/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

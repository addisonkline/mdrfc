import { apiFetch } from './client';
import type {
  GetRfcsResponse,
  GetRfcResponse,
  PostRfcResponse,
  PatchRfcResponse,
  CreateRfcData,
  UpdateRfcData,
} from '../types';

export async function listRfcs(): Promise<GetRfcsResponse> {
  return apiFetch<GetRfcsResponse>('/rfcs');
}

export async function getRfc(id: number): Promise<GetRfcResponse> {
  return apiFetch<GetRfcResponse>(`/rfc/${id}`);
}

export async function createRfc(data: CreateRfcData): Promise<PostRfcResponse> {
  return apiFetch<PostRfcResponse>('/rfc', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateRfc(id: number, data: UpdateRfcData): Promise<PatchRfcResponse> {
  return apiFetch<PatchRfcResponse>(`/rfc/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

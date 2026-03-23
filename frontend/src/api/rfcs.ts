import { apiFetch, buildApiPath } from './client';
import type {
  CreateRfcData,
  DeleteRfcResponse,
  GetRfcResponse,
  GetRfcsQuery,
  GetRfcsResponse,
  PostRfcResponse,
  PostRfcReviewResponse,
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

export async function requestRfcReview(id: number): Promise<PostRfcReviewResponse> {
  return apiFetch<PostRfcReviewResponse>(`/rfcs/${id}/review`, {
    method: 'POST',
  });
}

export async function quarantineRfc(id: number, reason: string): Promise<DeleteRfcResponse> {
  return apiFetch<DeleteRfcResponse>(buildApiPath(`/rfcs/${id}`, { reason }), {
    method: 'DELETE',
  });
}

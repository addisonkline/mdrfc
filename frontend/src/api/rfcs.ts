import { apiFetch, buildApiPath } from './client';
import type {
  CreateRfcData,
  DeleteRfcResponse,
  DeleteQuarantinedRfcResponse,
  GetRfcResponse,
  GetQuarantinedRfcsResponse,
  GetRfcsQuery,
  GetRfcsReviewNeededResponse,
  GetRfcsResponse,
  PatchRfcStatusData,
  PatchRfcStatusResponse,
  PostRfcResponse,
  PostQuarantinedRfcResponse,
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

export async function updateRfcStatus(
  id: number,
  data: PatchRfcStatusData,
): Promise<PatchRfcStatusResponse> {
  return apiFetch<PatchRfcStatusResponse>(`/rfcs/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function quarantineRfc(id: number, reason: string): Promise<DeleteRfcResponse> {
  return apiFetch<DeleteRfcResponse>(buildApiPath(`/rfcs/${id}`, { reason }), {
    method: 'DELETE',
  });
}

export async function getReviewNeededRfcs(): Promise<GetRfcsReviewNeededResponse> {
  return apiFetch<GetRfcsReviewNeededResponse>('/rfcs/review-needed');
}

export async function getQuarantinedRfcs(): Promise<GetQuarantinedRfcsResponse> {
  return apiFetch<GetQuarantinedRfcsResponse>('/rfcs/quarantined');
}

export async function restoreQuarantinedRfc(
  quarantineId: number,
): Promise<PostQuarantinedRfcResponse> {
  return apiFetch<PostQuarantinedRfcResponse>(`/rfcs/quarantined/${quarantineId}`, {
    method: 'POST',
  });
}

export async function deleteQuarantinedRfc(
  quarantineId: number,
): Promise<DeleteQuarantinedRfcResponse> {
  return apiFetch<DeleteQuarantinedRfcResponse>(`/rfcs/quarantined/${quarantineId}`, {
    method: 'DELETE',
  });
}

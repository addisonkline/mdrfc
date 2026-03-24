import { apiFetch } from './client';
import type {
  CreateRfcRevisionData,
  GetRfcRevisionResponse,
  GetRfcRevisionsResponse,
  PostRfcRevisionResponse,
} from '../types';

export async function listRfcRevisions(rfcId: number): Promise<GetRfcRevisionsResponse> {
  return apiFetch<GetRfcRevisionsResponse>(`/rfcs/${rfcId}/revs`);
}

export async function getRfcRevision(
  rfcId: number,
  revisionId: string,
): Promise<GetRfcRevisionResponse> {
  return apiFetch<GetRfcRevisionResponse>(`/rfcs/${rfcId}/revs/${revisionId}`);
}

export async function createRfcRevision(
  rfcId: number,
  data: CreateRfcRevisionData,
): Promise<PostRfcRevisionResponse> {
  return apiFetch<PostRfcRevisionResponse>(`/rfcs/${rfcId}/revs`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

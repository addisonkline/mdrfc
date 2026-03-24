import { apiFetch } from './client';
import type {
  CreateReadmeRevisionData,
  GetRfcsReadmeResponse,
  GetRfcsReadmeRevResponse,
  GetRfcsReadmeRevsResponse,
  PostRfcsReadmeRevResponse,
} from '../types';

export async function getReadme(): Promise<GetRfcsReadmeResponse> {
  return apiFetch<GetRfcsReadmeResponse>('/rfcs/README');
}

export async function listReadmeRevisions(): Promise<GetRfcsReadmeRevsResponse> {
  return apiFetch<GetRfcsReadmeRevsResponse>('/rfcs/README/revs');
}

export async function getReadmeRevision(
  revisionId: string,
): Promise<GetRfcsReadmeRevResponse> {
  return apiFetch<GetRfcsReadmeRevResponse>(`/rfcs/README/revs/${revisionId}`);
}

export async function createReadmeRevision(
  data: CreateReadmeRevisionData,
): Promise<PostRfcsReadmeRevResponse> {
  return apiFetch<PostRfcsReadmeRevResponse>('/rfcs/README/revs', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

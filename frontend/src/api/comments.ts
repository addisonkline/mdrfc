import { apiFetch, buildApiPath } from './client';
import type {
  DeleteQuarantinedCommentResponse,
  DeleteRfcCommentResponse,
  GetRfcCommentsResponse,
  GetRfcCommentResponse,
  GetQuarantinedCommentsResponse,
  PostRfcCommentResponse,
  PostCommentData,
  GetRfcCommentsQuery,
  PostQuarantinedCommentResponse,
} from '../types';

export async function getComments(
  rfcId: number,
  query: GetRfcCommentsQuery = {},
): Promise<GetRfcCommentsResponse> {
  return apiFetch<GetRfcCommentsResponse>(buildApiPath(`/rfcs/${rfcId}/comments`, query));
}

export async function getComment(rfcId: number, commentId: number): Promise<GetRfcCommentResponse> {
  return apiFetch<GetRfcCommentResponse>(`/rfcs/${rfcId}/comments/${commentId}`);
}

export async function postComment(data: PostCommentData): Promise<PostRfcCommentResponse> {
  const { rfc_id, ...body } = data;

  return apiFetch<PostRfcCommentResponse>(`/rfcs/${rfc_id}/comments`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function quarantineComment(
  rfcId: number,
  commentId: number,
  reason: string,
): Promise<DeleteRfcCommentResponse> {
  return apiFetch<DeleteRfcCommentResponse>(
    buildApiPath(`/rfcs/${rfcId}/comments/${commentId}`, { reason }),
    {
      method: 'DELETE',
    },
  );
}

export async function getQuarantinedComments(
  rfcId: number,
): Promise<GetQuarantinedCommentsResponse> {
  return apiFetch<GetQuarantinedCommentsResponse>(`/rfcs/${rfcId}/comments/quarantined`);
}

export async function restoreQuarantinedComment(
  rfcId: number,
  quarantineId: number,
): Promise<PostQuarantinedCommentResponse> {
  return apiFetch<PostQuarantinedCommentResponse>(
    `/rfcs/${rfcId}/comments/quarantined/${quarantineId}`,
    {
      method: 'POST',
    },
  );
}

export async function deleteQuarantinedComment(
  rfcId: number,
  quarantineId: number,
): Promise<DeleteQuarantinedCommentResponse> {
  return apiFetch<DeleteQuarantinedCommentResponse>(
    `/rfcs/${rfcId}/comments/quarantined/${quarantineId}`,
    {
      method: 'DELETE',
    },
  );
}

import { apiFetch, buildApiPath } from './client';
import type {
  GetRfcCommentsResponse,
  GetRfcCommentResponse,
  PostRfcCommentResponse,
  PostCommentData,
  GetRfcCommentsQuery,
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

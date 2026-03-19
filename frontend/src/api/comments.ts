import { apiFetch } from './client';
import type {
  GetRfcCommentsResponse,
  GetRfcCommentResponse,
  PostRfcCommentResponse,
  PostCommentData,
} from '../types';

export async function getComments(rfcId: number): Promise<GetRfcCommentsResponse> {
  return apiFetch<GetRfcCommentsResponse>(`/rfcs/${rfcId}/comments`);
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

import { apiFetch } from './client';
import type {
  GetRfcCommentsResponse,
  GetRfcCommentResponse,
  PostRfcCommentResponse,
  PostCommentData,
} from '../types';

export async function getComments(rfcId: number): Promise<GetRfcCommentsResponse> {
  return apiFetch<GetRfcCommentsResponse>(`/rfc/${rfcId}/comments`);
}

export async function getComment(rfcId: number, commentId: number): Promise<GetRfcCommentResponse> {
  return apiFetch<GetRfcCommentResponse>(`/rfc/${rfcId}/comment/${commentId}`);
}

export async function postComment(data: PostCommentData): Promise<PostRfcCommentResponse> {
  return apiFetch<PostRfcCommentResponse>('/rfc/comment', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

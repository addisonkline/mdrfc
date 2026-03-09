export type RFCStatus = 'draft' | 'open' | 'accepted' | 'rejected';

export interface RFCDocument {
  id: number;
  author_name_last: string;
  author_name_first: string;
  created_at: string;
  updated_at: string;
  title: string;
  slug: string;
  status: RFCStatus;
  content: string;
  summary: string;
}

export interface RFCDocumentSummary {
  id: number;
  author_name_last: string;
  author_name_first: string;
  created_at: string;
  updated_at: string;
  title: string;
  slug: string;
  status: RFCStatus;
  summary: string;
}

export interface CommentThread {
  id: number;
  parent_id: number | null;
  author_name_first: string;
  author_name_last: string;
  created_at: string;
  content: string;
  replies: CommentThread[];
}

export interface User {
  id: number;
  username: string;
  email: string;
  name_last: string;
  name_first: string;
  is_verified: boolean;
  verified_at: string | null;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface SignupData {
  username: string;
  email: string;
  name_first: string;
  name_last: string;
  password: string;
}

export interface CreateRfcData {
  title: string;
  slug: string;
  status: 'draft' | 'open';
  summary: string;
  content: string;
}

export interface UpdateRfcData {
  title?: string;
  slug?: string;
  status?: 'draft' | 'open';
  summary?: string;
  content?: string;
}

export interface PostCommentData {
  rfc_id: number;
  parent_comment_id: number | null;
  content: string;
}

// API response wrappers
export interface GetRfcsResponse {
  rfcs: RFCDocumentSummary[];
  metadata: Record<string, unknown>;
}

export interface GetRfcResponse {
  rfc: RFCDocument;
  metadata: Record<string, unknown>;
}

export interface PatchRfcResponse {
  rfc: RFCDocument;
  metadata: Record<string, unknown>;
}

export interface PostRfcResponse {
  rfc_id: number;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface PostSignupResponse {
  username: string;
  email: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface PostVerifyEmailResponse {
  username: string;
  email: string;
  verified_at: string;
  metadata: Record<string, unknown>;
}

export interface PostRfcCommentResponse {
  comment_id: number;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface GetRfcCommentsResponse {
  comment_threads: CommentThread[];
  metadata: Record<string, unknown>;
}

export interface GetRfcCommentResponse {
  comment: CommentThread;
  metadata: Record<string, unknown>;
}

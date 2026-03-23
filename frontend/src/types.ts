export type RFCStatus = 'draft' | 'open' | 'accepted' | 'rejected';
export type RfcListSort =
  | 'updated_at_desc'
  | 'updated_at_asc'
  | 'created_at_desc'
  | 'created_at_asc';
export type CommentListSort = 'created_at_asc' | 'created_at_desc';

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
  public: boolean;
  review_requested: boolean;
  reviewed: boolean;
  review_reason: string | null;
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
  public: boolean;
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

export interface PaginationMetadata {
  limit: number;
  offset: number;
  returned: number;
  total: number;
  has_more: boolean;
}

export interface GetRfcsFiltersMetadata {
  status: RFCStatus | null;
  public: boolean | null;
  author_id: number | null;
  review_requested: boolean | null;
}

export interface GetRfcsMetadata {
  pagination: PaginationMetadata;
  filters: GetRfcsFiltersMetadata;
  sort: RfcListSort;
}

export interface GetRfcCommentsMetadata {
  pagination: PaginationMetadata;
  filters: Record<string, never>;
  sort: CommentListSort;
}

export interface GetRfcsQuery {
  limit?: number;
  offset?: number;
  status?: RFCStatus;
  public?: boolean;
  author_id?: number;
  review_requested?: boolean;
  sort?: RfcListSort;
}

export interface GetRfcCommentsQuery {
  limit?: number;
  offset?: number;
  sort?: CommentListSort;
}

// API response wrappers
export interface GetRfcsResponse {
  rfcs: RFCDocumentSummary[];
  metadata: GetRfcsMetadata;
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
  metadata: GetRfcCommentsMetadata;
}

export interface GetRfcCommentResponse {
  comment: CommentThread;
  metadata: Record<string, unknown>;
}

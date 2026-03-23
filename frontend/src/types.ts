export type UUID = string;
export type RFCEditableStatus = 'draft' | 'open';
export type RFCStatus = RFCEditableStatus | 'accepted' | 'rejected';
export type RfcListSort =
  | 'updated_at_desc'
  | 'updated_at_asc'
  | 'created_at_desc'
  | 'created_at_asc';
export type CommentListSort = 'created_at_asc' | 'created_at_desc';

export interface User {
  id: number;
  username: string;
  email: string;
  name_last: string;
  name_first: string;
  is_verified: boolean;
  verified_at: string | null;
  created_at: string;
  is_admin: boolean;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface RFCDocument {
  id: number;
  author_id: number;
  author_name_last: string;
  author_name_first: string;
  created_at: string;
  updated_at: string;
  title: string;
  slug: string;
  status: RFCStatus;
  content: string;
  summary: string;
  revisions: UUID[];
  current_revision: UUID;
  agent_contributions: Record<string, string[]>;
  public: boolean;
  review_requested: boolean;
  reviewed: boolean;
  review_reason: string | null;
}

export interface RFCDocumentSummary {
  id: number;
  author_id: number;
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

export interface RFCRevisionSummary {
  id: UUID;
  rfc_id: number;
  created_at: string;
  author_name_last: string;
  author_name_first: string;
  agent_contributors: string[];
  message: string;
  public: boolean;
}

export interface RFCRevision {
  id: UUID;
  rfc_id: number;
  created_at: string;
  author_name_last: string;
  author_name_first: string;
  agent_contributors: string[];
  title: string;
  slug: string;
  status: RFCStatus;
  content: string;
  summary: string;
  message: string;
  public: boolean;
}

export interface RFCComment {
  id: number;
  parent_id: number | null;
  rfc_id: number;
  created_at: string;
  content: string;
  author_name_first: string;
  author_name_last: string;
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

export interface QuarantinedRFCSummary {
  quarantine_id: number;
  quarantined_by_name_last: string;
  quarantined_by_name_first: string;
  quarantined_at: string;
  reason: string;
  rfc_id: number;
  rfc_title: string;
  rfc_slug: string;
  rfc_status: RFCStatus;
  rfc_summary: string;
}

export interface QuarantinedComment {
  quarantine_id: number;
  quarantined_by_name_last: string;
  quarantined_by_name_first: string;
  quarantined_at: string;
  reason: string;
  comment: RFCComment;
}

export interface RFCReadme {
  content: string;
  created_at: string;
  updated_at: string;
  current_revision: UUID;
  revisions: UUID[];
  public: boolean;
}

export interface RFCReadmeRevisionSummary {
  revision_id: UUID;
  created_at: string;
  created_by_name_last: string;
  created_by_name_first: string;
  reason: string;
  public: boolean;
}

export interface RFCReadmeRevision {
  revision_id: UUID;
  created_at: string;
  created_by_name_last: string;
  created_by_name_first: string;
  reason: string;
  content: string;
  public: boolean;
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
  status: RFCEditableStatus;
  summary: string;
  content: string;
  agent_contributors: string[];
  public: boolean;
}

export interface RFCRevisionUpdateData {
  title?: string;
  slug?: string;
  status?: RFCEditableStatus;
  summary?: string;
  content?: string;
  agent_contributors?: string[];
  public?: boolean;
}

export interface CreateRfcRevisionData {
  update: RFCRevisionUpdateData;
  message: string;
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

export interface GetRfcsResponse {
  rfcs: RFCDocumentSummary[];
  metadata: GetRfcsMetadata;
}

export interface GetRfcResponse {
  rfc: RFCDocument;
  metadata: Record<string, unknown>;
}

export interface PostRfcResponse {
  rfc_id: number;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface DeleteRfcResponse {
  message: string;
  quarantined_at: string;
  metadata: Record<string, unknown>;
}

export interface GetRfcRevisionsResponse {
  revisions: RFCRevisionSummary[];
  metadata: Record<string, unknown>;
}

export interface GetRfcRevisionResponse {
  revision: RFCRevision;
  metadata: Record<string, unknown>;
}

export interface PostRfcRevisionResponse {
  revision: RFCRevision;
  metadata: Record<string, unknown>;
}

export interface PostRfcReviewResponse {
  message: string;
  requested_at: string;
  metadata: Record<string, unknown>;
}

export interface SignupResponseMetadata {
  verification_required: boolean;
  verification_expires_at: string;
  verification_token: string | null;
}

export interface PostSignupResponse {
  username: string;
  email: string;
  created_at: string;
  metadata: SignupResponseMetadata;
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

export interface GetQuarantinedRfcsResponse {
  quarantined_rfcs: QuarantinedRFCSummary[];
  metadata: Record<string, unknown>;
}

export interface GetQuarantinedCommentsResponse {
  quarantined_comments: QuarantinedComment[];
  metadata: Record<string, unknown>;
}

export interface DeleteQuarantinedRfcResponse {
  message: string;
  deleted_at: string;
  metadata: Record<string, unknown>;
}

export interface PostQuarantinedRfcResponse {
  message: string;
  unquarantined_at: string;
  metadata: Record<string, unknown>;
}

export interface DeleteQuarantinedCommentResponse {
  message: string;
  deleted_at: string;
  metadata: Record<string, unknown>;
}

export interface PostQuarantinedCommentResponse {
  message: string;
  unquarantined_at: string;
  metadata: Record<string, unknown>;
}

export interface GetRfcsReviewNeededResponse {
  message: string;
  rfcs: RFCDocumentSummary[];
  metadata: Record<string, unknown>;
}

export interface GetRfcsReadmeResponse {
  message: string;
  readme: RFCReadme;
  metadata: Record<string, unknown>;
}

export interface GetRfcsReadmeRevsResponse {
  message: string;
  revisions: RFCReadmeRevisionSummary[];
  metadata: Record<string, unknown>;
}

export interface GetRfcsReadmeRevResponse {
  message: string;
  revision: RFCReadmeRevision;
  metadata: Record<string, unknown>;
}

export interface PostRfcsReadmeRevResponse {
  message: string;
  revision: RFCReadmeRevision;
  metadata: Record<string, unknown>;
}

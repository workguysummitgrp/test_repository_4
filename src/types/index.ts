/**TypeScript types for the onboarding portal — mirrors backend Pydantic schemas.*/

export type UserRole = "customer" | "reviewer" | "approver" | "admin" | "compliance";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  status: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  role: UserRole;
  user_id: number;
}

export type ApplicationStatus =
  | "draft"
  | "submitted"
  | "under_evaluation"
  | "under_review"
  | "approved"
  | "rejected";

export interface Application {
  id: number;
  application_id: string;
  user_id: number;
  status: ApplicationStatus;
  form_data: Record<string, unknown>;
  form_schema_version: string;
  submitted_at: string | null;
  decision_at: string | null;
  final_decision: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApplicationList {
  items: Application[];
  total: number;
  page: number;
  size: number;
}

export interface Draft {
  id: number;
  user_id: number;
  form_data: Record<string, unknown>;
  current_step: number;
  last_saved_at: string;
}

export interface DocumentInfo {
  id: number;
  application_id: number;
  file_name: string;
  file_type: string;
  file_size_bytes: number;
  status: string;
  uploaded_at: string | null;
  created_at: string;
}

export interface EvaluationInfo {
  id: number;
  application_id: number;
  score: number;
  confidence: string;
  summary: string;
  flags: string[];
  model_version: string;
  temperature: number;
  retry_count: number;
  is_valid: boolean;
  evaluated_at: string;
}

export interface ReviewerDecisionInfo {
  id: number;
  application_id: number;
  reviewer_id: number;
  decision: string;
  comment: string | null;
  assigned_at: string;
  decided_at: string | null;
}

export interface ApproverDecisionInfo {
  id: number;
  application_id: number;
  approver_id: number;
  decision: string;
  comment: string;
  source: string;
  assigned_at: string;
  decided_at: string | null;
}

export interface NotificationInfo {
  id: number;
  user_id: number;
  application_id: number | null;
  channel: string;
  event_type: string;
  subject: string;
  body: string;
  is_read: boolean;
  sent_at: string;
  read_at: string | null;
}

export interface NotificationList {
  items: NotificationInfo[];
  total: number;
  unread_count: number;
}

export interface AuditLogEntry {
  id: number;
  application_id: number | null;
  actor_id: number | null;
  actor_type: string;
  action: string;
  before_state: Record<string, unknown> | null;
  after_state: Record<string, unknown> | null;
  rationale: string | null;
  created_at: string;
}

export interface ThresholdConfig {
  id: number;
  band_name: string;
  min_score: number;
  max_score: number;
}

export interface WorkflowConfig {
  id: number;
  node_name: string;
  is_enabled: boolean;
}

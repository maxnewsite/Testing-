export enum UserRole {
  CLIENT = 'client',
  PANELIST = 'panelist',
  ADMIN = 'admin',
}

export enum PollStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  ARCHIVED = 'archived',
}

export enum QuestionType {
  AB_TEST = 'ab_test',
  RANKING = 'ranking',
  OPEN_ENDED = 'open_ended',
  MULTIPLE_CHOICE = 'multiple_choice',
  RATING_SCALE = 'rating_scale',
  IMAGE_CHOICE = 'image_choice',
  VIDEO_RESPONSE = 'video_response',
}

export interface User {
  id: number;
  email: string;
  full_name?: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
}

export interface Question {
  id: number;
  poll_id: number;
  question_type: QuestionType;
  order: number;
  text: string;
  description?: string;
  options: string[];
  media_urls: string[];
  is_required: boolean;
  validation_rules: Record<string, any>;
  is_attention_check: boolean;
  expected_answer?: string;
  created_at: string;
}

export interface Poll {
  id: number;
  owner_id: number;
  title: string;
  description?: string;
  status: PollStatus;
  target_responses: number;
  cost_per_response: number;
  estimated_duration_minutes: number;
  targeting_rules: Record<string, any>;
  response_count: number;
  completion_rate: number;
  average_quality_score: number;
  created_at: string;
  updated_at: string;
  published_at?: string;
  completed_at?: string;
  questions: Question[];
}

export interface ResponseAnswer {
  question_id: number;
  answer_text?: string;
  answer_choice?: string;
  answer_data?: Record<string, any>;
  time_spent_seconds?: number;
}

export interface Response {
  id: number;
  poll_id: number;
  panel_member_id: number;
  started_at: string;
  submitted_at?: string;
  time_spent_seconds?: number;
  is_complete: boolean;
  is_validated: boolean;
  is_flagged: boolean;
  quality_score: number;
  is_paid: boolean;
  payment_amount?: number;
  answers: ResponseAnswer[];
}

export interface PanelMember {
  id: number;
  user_id: number;
  date_of_birth?: string;
  gender?: string;
  location_country?: string;
  location_state?: string;
  location_city?: string;
  zip_code?: string;
  is_qualified: boolean;
  qualification_level: number;
  is_suspended: boolean;
  total_responses: number;
  total_earnings: number;
  average_quality_score: number;
  response_rate: number;
  completion_rate: number;
  wallet_balance: number;
  joined_at: string;
  last_active_at?: string;
  profile_completeness: number;
}

export interface Payment {
  id: number;
  user_id: number;
  poll_id?: number;
  payment_type: string;
  status: string;
  amount: number;
  currency: string;
  stripe_payment_intent_id?: string;
  description?: string;
  created_at: string;
  completed_at?: string;
}

export interface Payout {
  id: number;
  panel_member_id: number;
  amount: number;
  currency: string;
  status: string;
  payout_method: string;
  payout_email?: string;
  requested_at: string;
  processed_at?: string;
  completed_at?: string;
}

export interface AnalyticsSummary {
  poll_id: number;
  total_responses: number;
  completed_responses: number;
  validated_responses: number;
  flagged_responses: number;
  completion_rate: number;
  average_quality_score: number;
  average_time_minutes: number;
  target_responses: number;
  progress_percentage: number;
}

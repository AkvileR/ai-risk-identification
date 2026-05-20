import { EXCLUSION_LABELS, ROLE_LABELS } from "./constants";

export type Role =
  | "provider"
  | "deployer"
  | "distributor"
  | "importer"
  | "product_manufacturer"
  | "authorised_representative";

export function formatRole(role: Role | string): string {
  return ROLE_LABELS[role as Role] ?? role;
}

export type ExclusionType =
  | "military"
  | "third_country_le"
  | "research"
  | "open_source"
  | "personal"
  | "high_risk_exception";

export function formatExclusion(exclusion: ExclusionType | string): string {
  return EXCLUSION_LABELS[exclusion as ExclusionType] ?? exclusion;
}

export type RiskTier = "Prohibited" | "High" | "Limited" | "Minimal" | "Out of Scope";

export type Applies = "yes" | "no" | "uncertain";

export interface SystemDescription {
  raw_input: string;
  role: Role;
  is_gpai: boolean;
  in_eu_scope: boolean;
  exclusions: ExclusionType[];
}

export type AmbiguityType = "terminology" | "underspecified" | "scope";

export interface ClarificationExchange {
  question: string;
  answer: string;
}

export interface CriterionFinding {
  criterion_id: string;
  article_ref: string;
  question: string;
  applies: Applies;
  confidence_score: number;
  reasoning: string;
  clarification_history: ClarificationExchange[];
  clarification_round_count: number;
  extracted_value: Record<string, unknown> | null;
}

export interface RunSummary {
  risk_tier: RiskTier;
  criteria_evaluated_total: number;
  clarification_rounds_total: number;
  unique_criteria_clarified: number;
  clarified_criterion_ids: string[];
}

export interface Verdict {
  role: Role;
  detected_role: Role;
  risk_tier: RiskTier;
  tier_reasoning: string;
  is_gpai: boolean;
  is_gpai_systemic: boolean;
  exclusions: ExclusionType[];
  applicable_findings: CriterionFinding[];
  non_applicable_findings: CriterionFinding[];
  uncertain_findings: CriterionFinding[];
  article_citations: string[];
  run_summary: RunSummary;
}

export interface AppState extends Record<string, unknown> {
  user_input: string;
  system_description: SystemDescription | null;
  criterion_findings: Record<string, CriterionFinding>;
  active_phase: string;
  pending_assessments: string[];
  verdict: Verdict | null;
}

export interface ClarificationQuestion {
  criterion_id: string;
  article_ref: string;
  ambiguity_type: AmbiguityType;
  question: string;
}

export interface ClarificationPayload {
  kind: "criterion_clarifications";
  questions: ClarificationQuestion[];
}

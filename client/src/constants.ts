import type { Applies, ExclusionType, Role, RiskTier } from "./types";

export const MAX_CLARIFICATION_CHARS = 200;
export const MAX_INPUT_CHARS = 2000;

export const PLACEHOLDER =
  "e.g.: A CV-screening tool for hiring deployed in Germany.";

export const PHASE_LABELS: Record<string, string> = {
  defining_system: "Identifying your system",
  asking_clarification: "Waiting for your clarification",
  evaluating_criteria: "Evaluating EU AI Act criteria",
  synthesis: "Deriving the risk tier and obligations",
};

export const STATUS_MARK: Record<Applies, string> = {
  yes: "✓",
  no: "·",
  uncertain: "?",
};

export const STATUS_LABEL: Record<Applies, string> = {
  yes: "Applies",
  no: "Does not apply",
  uncertain: "Uncertain",
};

export const SYSTEM_SCOPE_CRITERION_IDS: string[] = [
  "art3_entity_role",
  "art2_provider_places_ai_eu",
  "art2_provider_places_gpai_eu",
  "art2_deployer_established_eu",
  "art2_importer_third_country_trademark",
  "art2_output_used_in_eu",
  "art2_exclusions",
];

export const ARTICLE_ORDER: string[] = [
  "Art. 3",
  "Art. 2",
  "Art. 25(3)",
  "Annex I §A",
  "Annex I §B",
  "Art. 6(1)(b)",
  "Art. 6(3)",
  "Annex III §1",
  "Annex III §2",
  "Annex III §3",
  "Annex III §4",
  "Annex III §5",
  "Annex III §6",
  "Annex III §7",
  "Annex III §8",
  "Art. 51",
  "Art. 5(1)(a)",
  "Art. 5(1)(b)",
  "Art. 5(1)(c)",
  "Art. 5(1)(d)",
  "Art. 5(1)(e)",
  "Art. 5(1)(f)",
  "Art. 5(1)(g)",
  "Art. 5(1)(h)",
  "Art. 50(1)",
  "Art. 50(2)",
  "Art. 50(3)",
  "Art. 50(4)",
];

export const TIER_CLASSNAME: Record<RiskTier, string> = {
  Critical: "tier-badge tier-critical",
  High: "tier-badge tier-high",
  Limited: "tier-badge tier-limited",
  Low: "tier-badge tier-low",
  "Out of Scope": "tier-badge tier-out-of-scope",
};

export const ROLE_LABELS: Record<Role, string> = {
  provider: "Provider",
  deployer: "Deployer",
  distributor: "Distributor",
  importer: "Importer",
  product_manufacturer: "Product Manufacturer",
  authorised_representative: "Authorised Representative",
};

export const EXCLUSION_LABELS: Record<ExclusionType, string> = {
  military: "Military",
  third_country_le: "Third-country law enforcement",
  research: "Research",
  open_source: "Open source",
  personal: "Personal use",
  high_risk_exception: "High-risk exception",
};

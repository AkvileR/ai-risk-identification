import { CriterionFinding, formatRole } from "../types";
import { ARTICLE_ORDER } from "../constants";

export interface ArticleGroup {
  article_ref: string;
  findings: CriterionFinding[];
}

const ORDER_INDEX: Record<string, number> = Object.fromEntries(
  ARTICLE_ORDER.map((ref, i) => [ref, i]),
);

function articleRank(ref: string): number {
  const known = ORDER_INDEX[ref];
  return known !== undefined ? known : ARTICLE_ORDER.length;
}

export function groupByArticle(
  findings: Record<string, CriterionFinding>,
): ArticleGroup[] {
  const groups = new Map<string, CriterionFinding[]>();
  for (const finding of Object.values(findings)) {
    const existing = groups.get(finding.article_ref);
    if (existing) {
      existing.push(finding);
    } else {
      groups.set(finding.article_ref, [finding]);
    }
  }

  const result: ArticleGroup[] = [];
  for (const [article_ref, list] of groups.entries()) {
    list.sort((a, b) => a.criterion_id.localeCompare(b.criterion_id));
    result.push({ article_ref, findings: list });
  }
  result.sort((a, b) => {
    const ra = articleRank(a.article_ref);
    const rb = articleRank(b.article_ref);
    if (ra !== rb) return ra - rb;
    return a.article_ref.localeCompare(b.article_ref);
  });
  return result;
}

export function isExtractionFinding(finding: CriterionFinding): boolean {
  const value = finding.extracted_value;
  if (value === null || typeof value !== "object") return false;
  return "role" in value;
}

export function extractionStatusLabel(finding: CriterionFinding): string {
  const value = finding.extracted_value;
  if (value === null || typeof value !== "object") return "";
  if ("role" in value && typeof value.role === "string") {
    return formatRole(value.role);
  }
  return "";
}

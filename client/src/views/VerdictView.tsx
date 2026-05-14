import React from "react";
import { Applies, CriterionFinding, Verdict, formatExclusion } from "../types";
import { SYSTEM_SCOPE_CRITERION_IDS } from "../constants";
import { TierBadge } from "../components/TierBadge";
import { FindingCard } from "../components/FindingCard";
import {
  extractionStatusLabel,
  groupByArticle,
  isExtractionFinding,
} from "./grouping";

const SCOPE_ANSWER_LABEL: Record<Applies, string> = {
  yes: "Yes",
  no: "No",
  uncertain: "Uncertain",
};

interface Props {
  verdict: Verdict;
  findings: Record<string, CriterionFinding>;
  onReset: () => void;
}

function toRecord(list: CriterionFinding[]): Record<string, CriterionFinding> {
  const out: Record<string, CriterionFinding> = {};
  for (const f of list) out[f.criterion_id] = f;
  return out;
}

function ScopeCard({ finding }: { finding: CriterionFinding }) {
  const answer = isExtractionFinding(finding)
    ? extractionStatusLabel(finding)
    : SCOPE_ANSWER_LABEL[finding.applies];
  return (
    <details className="scope-card">
      <summary className="scope-summary">
        <span className="scope-question">{finding.question}</span>
        <span className="scope-answer">{answer}</span>
      </summary>
      <div className="scope-body">
        <p className="finding-reasoning">{finding.reasoning}</p>
        <div className="finding-footer">
          <span className="finding-confidence">
            confidence {Math.round(finding.confidence_score * 100)}%
          </span>
          <span className="finding-criterion">{finding.criterion_id}</span>
        </div>
      </div>
    </details>
  );
}

function ArticleGroupedFindings({ findings }: { findings: CriterionFinding[] }) {
  const groups = groupByArticle(toRecord(findings));
  return (
    <div className="finding-groups">
      {groups.map((g) => (
        <details key={g.article_ref} className="finding-group">
          <summary className="finding-group-header">
            {g.article_ref}
            <span className="finding-group-count">{g.findings.length}</span>
          </summary>
          <div className="finding-grid">
            {g.findings.map((f) => (
              <FindingCard key={f.criterion_id} finding={f} />
            ))}
          </div>
        </details>
      ))}
    </div>
  );
}

export function VerdictView({ verdict, findings, onReset }: Props) {
  const scopeFindings = SYSTEM_SCOPE_CRITERION_IDS
    .map((id) => findings[id])
    .filter((f): f is CriterionFinding => f !== undefined);

  return (
    <div className="verdict-view">
      <header className="verdict-header">
        <TierBadge tier={verdict.risk_tier} />
        <h1>This system is classified as {verdict.risk_tier} Risk.</h1>
        <button className="verdict-reset" onClick={onReset}>
          New assessment
        </button>
      </header>

      {verdict.exclusions.length > 0 && (
        <div className="verdict-exclusions">
          <span className="verdict-exclusions-label">Exclusions:</span>
          {verdict.exclusions.map((ex) => (
            <span key={ex} className="exclusion-chip">
              {formatExclusion(ex)}
            </span>
          ))}
        </div>
      )}

      <section className="verdict-section">
        <h2>Why?</h2>
        <pre className="tier-reasoning">{verdict.tier_reasoning}</pre>
      </section>

      {scopeFindings.length > 0 && (
        <section className="verdict-section">
          <h2>System scope</h2>
          <div className="scope-grid">
            {scopeFindings.map((f) => (
              <ScopeCard key={f.criterion_id} finding={f} />
            ))}
          </div>
        </section>
      )}

      <section className="verdict-section">
        <h2>Applicable findings ({verdict.applicable_findings.length})</h2>
        {verdict.applicable_findings.length === 0 ? (
          <p>No criteria applied to this system.</p>
        ) : (
          <ArticleGroupedFindings findings={verdict.applicable_findings} />
        )}
      </section>

      {verdict.uncertain_findings.length > 0 && (
        <section className="verdict-section">
          <details>
            <summary>
              Uncertain ({verdict.uncertain_findings.length}) — model could
              not decide after clarification rounds
            </summary>
            <ArticleGroupedFindings findings={verdict.uncertain_findings} />
          </details>
        </section>
      )}

      {verdict.non_applicable_findings.length > 0 && (
        <section className="verdict-section">
          <details>
            <summary>
              Not applicable ({verdict.non_applicable_findings.length}) —
              criteria the model determined did not apply
            </summary>
            <ArticleGroupedFindings findings={verdict.non_applicable_findings} />
          </details>
        </section>
      )}

    </div>
  );
}

import React from "react";
import { Verdict, formatRole, formatExclusion } from "../types";
import { TierBadge } from "../components/TierBadge";
import { FindingCard } from "../components/FindingCard";

interface Props {
  verdict: Verdict;
  onReset: () => void;
}

export function VerdictView({ verdict, onReset }: Props) {
  const roleEscalated = verdict.role !== verdict.detected_role;

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

      <section className="verdict-section">
        <h2>Applicable findings ({verdict.applicable_findings.length})</h2>
        {verdict.applicable_findings.length === 0 ? (
          <p>No criteria applied to this system.</p>
        ) : (
          <div className="finding-grid">
            {verdict.applicable_findings.map((f) => (
              <FindingCard key={f.criterion_id} finding={f} />
            ))}
          </div>
        )}
      </section>

      {verdict.uncertain_findings.length > 0 && (
        <section className="verdict-section">
          <details>
            <summary>
              Uncertain ({verdict.uncertain_findings.length}) — model could
              not decide after clarification rounds
            </summary>
            <div className="finding-grid">
              {verdict.uncertain_findings.map((f) => (
                <FindingCard key={f.criterion_id} finding={f} />
              ))}
            </div>
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
            <div className="finding-grid">
              {verdict.non_applicable_findings.map((f) => (
                <FindingCard key={f.criterion_id} finding={f} />
              ))}
            </div>
          </details>
        </section>
      )}

      <section className="verdict-meta">
        {roleEscalated ? (
          <span>
            Detected as {formatRole(verdict.detected_role)}; reclassified as{" "}
            {formatRole(verdict.role)}
          </span>
        ) : (
          <span>Role: {formatRole(verdict.role)}</span>
        )}
        <span>GPAI: {verdict.is_gpai ? "yes" : "no"}</span>
        {verdict.is_gpai_systemic && <span>Systemic risk: yes</span>}
      </section>
    </div>
  );
}

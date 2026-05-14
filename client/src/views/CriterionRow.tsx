import React from "react";
import { CriterionFinding } from "../types";
import { STATUS_LABEL, STATUS_MARK } from "../constants";
import { extractionStatusLabel, isExtractionFinding } from "./grouping";

interface Props {
  finding: CriterionFinding;
}

export function CriterionRow({ finding }: Props) {
  const confidencePct = Math.round(finding.confidence_score * 100);
  const extraction = isExtractionFinding(finding);
  const rowClass = extraction
    ? "criterion-row criterion-extraction"
    : `criterion-row criterion-${finding.applies}`;
  const mark = extraction ? "ℹ" : STATUS_MARK[finding.applies];
  const status = extraction
    ? extractionStatusLabel(finding)
    : STATUS_LABEL[finding.applies];

  return (
    <details className={rowClass}>
      <summary className="criterion-summary">
        <span className="criterion-mark" aria-hidden>
          {mark}
        </span>
        <span className="criterion-question">{finding.question}</span>
        <span className="criterion-status">{status}</span>
      </summary>
      <div className="criterion-body">
        <p className="criterion-full-question">{finding.question}</p>
        <p className="criterion-reasoning">{finding.reasoning}</p>
        <div className="criterion-meta">
          <span>confidence {confidencePct}%</span>
          <span className="criterion-id">{finding.criterion_id}</span>
        </div>
      </div>
    </details>
  );
}

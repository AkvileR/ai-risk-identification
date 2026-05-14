import React from "react";
import { CriterionFinding } from "../types";

interface Props {
  finding: CriterionFinding;
}

export function FindingCard({ finding }: Props) {
  return (
    <div className="finding-card">
      <p className="finding-question">{finding.question}</p>
      <p className="finding-reasoning">{finding.reasoning}</p>
      <div className="finding-footer">
        <span className="finding-confidence">
          confidence {Math.round(finding.confidence_score * 100)}%
        </span>
        <span className="finding-criterion">{finding.criterion_id}</span>
      </div>
    </div>
  );
}

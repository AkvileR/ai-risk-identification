import React from "react";
import { CriterionFinding } from "../types";

interface Props {
  finding: CriterionFinding;
}

export function FindingCard({ finding }: Props) {
  return (
    <div className="finding-card">
      <div className="finding-header">
        <span className="finding-article">[{finding.article_ref}]</span>
        <span className="finding-confidence">
          confidence {Math.round(finding.confidence_score * 100)}%
        </span>
      </div>
      <div className="finding-criterion">{finding.criterion_id}</div>
      <p className="finding-reasoning">{finding.reasoning}</p>
    </div>
  );
}

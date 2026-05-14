import React from "react";
import { ArticleGroup, isExtractionFinding } from "./grouping";
import { CriterionRow } from "./CriterionRow";

interface Props {
  group: ArticleGroup;
  defaultOpen?: boolean;
}

export function ArticleSection({ group, defaultOpen = false }: Props) {
  const total = group.findings.length;
  const booleanFindings = group.findings.filter((f) => !isExtractionFinding(f));
  const applied = booleanFindings.filter((f) => f.applies === "yes").length;
  const uncertain = booleanFindings.filter((f) => f.applies === "uncertain").length;

  return (
    <details className="article-section" open={defaultOpen}>
      <summary className="article-summary">
        <span className="article-ref">{group.article_ref}</span>
        <span className="article-counts">
          {applied > 0 && <span className="article-count-applied">{applied} apply</span>}
          {uncertain > 0 && (
            <span className="article-count-uncertain">{uncertain} uncertain</span>
          )}
          <span className="article-count-total">{total} evaluated</span>
        </span>
      </summary>
      <div className="article-body">
        {group.findings.map((f) => (
          <CriterionRow key={f.criterion_id} finding={f} />
        ))}
      </div>
    </details>
  );
}

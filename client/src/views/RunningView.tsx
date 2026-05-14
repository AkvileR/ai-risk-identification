import React from "react";
import {
  CriterionFinding,
  SystemDescription,
  formatExclusion,
  formatRole,
} from "../types";
import { PHASE_LABELS } from "../constants";
import { groupByArticle } from "./grouping";
import { ArticleSection } from "./ArticleSection";

interface Props {
  findings: Record<string, CriterionFinding>;
  activePhase: string;
  systemDescription: SystemDescription | null;
  isLoading: boolean;
  isWaitingForUser: boolean;
  onResumeClarification: (() => void) | null;
}

function phaseLabel(activePhase: string): string {
  if (!activePhase) return "Starting…";
  return PHASE_LABELS[activePhase] ?? activePhase;
}

export function RunningView({
  findings,
  activePhase,
  systemDescription,
  isLoading,
  isWaitingForUser,
  onResumeClarification,
}: Props) {
  const evaluated = Object.keys(findings).length;
  const groups = groupByArticle(findings);

  let statusLabel: string;
  if (isWaitingForUser) {
    statusLabel = "Waiting for your input";
  } else if (isLoading) {
    statusLabel = phaseLabel(activePhase);
  } else {
    statusLabel = "Stopped";
  }

  return (
    <div className="running-view">
      <div className="running-status">
        {isLoading && !isWaitingForUser && <span className="spinner" />}
        <span className="running-status-text">{statusLabel}</span>
        {onResumeClarification && (
          <button
            type="button"
            className="resume-clarification"
            onClick={onResumeClarification}
          >
            Resume clarification
          </button>
        )}
      </div>

      {systemDescription && (
        <div className="system-card">
          <div className="system-card-row">
            <span className="system-card-label">Role</span>
            <span className="system-card-value">
              {formatRole(systemDescription.role)}
            </span>
          </div>
          <div className="system-card-row">
            <span className="system-card-label">GPAI</span>
            <span className="system-card-value">
              {systemDescription.is_gpai ? "yes" : "no"}
            </span>
          </div>
          <div className="system-card-row">
            <span className="system-card-label">EU scope</span>
            <span className="system-card-value">
              {systemDescription.in_eu_scope ? "in scope" : "out of scope"}
            </span>
          </div>
          {systemDescription.exclusions.length > 0 && (
            <div className="system-card-row system-card-row-block">
              <span className="system-card-label">Exclusions</span>
              <span className="system-card-chips">
                {systemDescription.exclusions.map((ex) => (
                  <span key={ex} className="exclusion-chip">
                    {formatExclusion(ex)}
                  </span>
                ))}
              </span>
            </div>
          )}
        </div>
      )}

      <div className="elapsed-count">
        {evaluated === 0
          ? "No criteria evaluated yet"
          : `${evaluated} ${evaluated === 1 ? "criterion" : "criteria"} evaluated`}
      </div>

      {groups.length > 0 && (
        <div className="article-list">
          {groups.map((g) => (
            <ArticleSection key={g.article_ref} group={g} />
          ))}
        </div>
      )}
    </div>
  );
}

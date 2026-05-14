import React from "react";
import { ClarificationPayload } from "../types";
import { MAX_CLARIFICATION_CHARS } from "../constants";

interface Props {
  payload: ClarificationPayload;
  index: number;
  answers: Record<string, string>;
  onIndexChange: (next: number) => void;
  onAnswersChange: (next: Record<string, string>) => void;
  onAnswer: (answers: Record<string, string>) => void;
  onClose: () => void;
}

export function ClarificationModal({
  payload,
  index,
  answers,
  onIndexChange,
  onAnswersChange,
  onAnswer,
  onClose,
}: Props) {
  const questions = payload.questions;
  const total = questions.length;

  const safeIndex = Math.min(Math.max(index, 0), total - 1);
  const current = questions[safeIndex];
  const currentAnswer = answers[current.criterion_id] ?? "";
  const isLast = safeIndex === total - 1;
  const trimmed = currentAnswer.trim();

  const handleNext = (e: React.FormEvent) => {
    e.preventDefault();
    if (!trimmed) return;
    const nextAnswers = { ...answers, [current.criterion_id]: trimmed };
    onAnswersChange(nextAnswers);
    if (isLast) {
      onAnswer(nextAnswers);
    } else {
      onIndexChange(safeIndex + 1);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <button
          className="modal-close"
          type="button"
          onClick={onClose}
          aria-label="Close"
        >
          ×
        </button>
        <h2>
          Need clarification ({safeIndex + 1} of {total})
        </h2>
        <div className="modal-question-meta">
          <span className="modal-question-article">[{current.article_ref}]</span>
          <span className="modal-question-criterion">{current.criterion_id}</span>
        </div>
        <p className="modal-question">{current.question}</p>
        <form onSubmit={handleNext}>
          <textarea
            key={current.criterion_id}
            className="modal-textarea"
            value={currentAnswer}
            onChange={(e) =>
              onAnswersChange({
                ...answers,
                [current.criterion_id]: e.target.value,
              })
            }
            rows={4}
            autoFocus
            placeholder="Your answer…"
            maxLength={MAX_CLARIFICATION_CHARS}
          />
          <div className="modal-actions">
            <span className="char-counter">
              {currentAnswer.length} / {MAX_CLARIFICATION_CHARS}
            </span>
            <button
              type="submit"
              className="modal-submit"
              disabled={!trimmed}
            >
              {isLast ? "Submit" : "Next →"}
            </button>
          </div>
        </form>
        <div className="modal-progress-dots" aria-hidden>
          {questions.map((q, i) => (
            <span
              key={q.criterion_id}
              className={i === safeIndex ? "dot dot-active" : "dot"}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

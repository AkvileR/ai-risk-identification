import React, { useState } from "react";
import { ClarificationPayload } from "../types";
import { MAX_CLARIFICATION_CHARS } from "../constants";

interface Props {
  payload: ClarificationPayload;
  onAnswer: (answers: Record<string, string>) => void;
  onClose: () => void;
}

export function ClarificationModal({ payload, onAnswer, onClose }: Props) {
  const questions = payload.questions;
  const total = questions.length;

  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const current = questions[index];
  const currentAnswer = answers[current.criterion_id] ?? "";
  const isLast = index === total - 1;
  const trimmed = currentAnswer.trim();

  const handleNext = (e: React.FormEvent) => {
    e.preventDefault();
    if (!trimmed) return;
    const nextAnswers = { ...answers, [current.criterion_id]: trimmed };
    setAnswers(nextAnswers);
    if (isLast) {
      onAnswer(nextAnswers);
    } else {
      setIndex(index + 1);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <button
          className="modal-close"
          type="button"
          onClick={onClose}
          aria-label="Stop assessment"
        >
          ×
        </button>
        <h2>
          Need clarification ({index + 1} of {total})
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
              setAnswers({ ...answers, [current.criterion_id]: e.target.value })
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
              className={i === index ? "dot dot-active" : "dot"}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

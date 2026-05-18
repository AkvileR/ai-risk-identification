import React, { useState } from "react";
import { MAX_INPUT_CHARS, PLACEHOLDER } from "../constants";

export type InputPhase = "idle" | "running" | "stopped";

interface Props {
  phase: InputPhase;
  submittedText?: string | null;
  onSubmit: (text: string) => void;
  onStop: () => void;
  onReset: () => void;
}

export function InputView({
  phase,
  submittedText,
  onSubmit,
  onStop,
  onReset,
}: Props) {
  const [text, setText] = useState("");

  if (phase === "idle") {
    const trimmed = text.trim();

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      if (!trimmed) return;
      onSubmit(trimmed);
    };

    return (
      <form className="input-view" onSubmit={handleSubmit}>
        <h1>EU AI Act Risk Identification <span className="prototype-suffix">Prototype</span></h1>
        <p className="input-hint">
          Describe your AI system. The assessor will evaluate your input against a maximum of 51 criteria to determine your risk group.
        </p>
        <p className="input-hint">
          The assessment will take a few minutes to complete and you may be asked to clarify missing facts.
        </p>
        <p className="input-hint">
          Since this is an early prototype, if you run into any issues please reload the page and restart the assessment.
        </p>
        <textarea
          className="input-textarea"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={PLACEHOLDER}
          rows={8}
          maxLength={MAX_INPUT_CHARS}
        />
        <div className="input-footer">
          <span className="char-counter">
            {text.length} / {MAX_INPUT_CHARS}
          </span>
          <button
            className="input-submit"
            type="submit"
            disabled={!trimmed}
          >
            Assess
          </button>
        </div>
      </form>
    );
  }

  return (
    <div className="input-view input-view-collapsed">
      <h1>EU AI Act Risk Identification <span className="prototype-suffix">Prototype</span></h1>
      <div className="input-readonly">
        {submittedText || "(no description)"}
      </div>
      {phase === "running" ? (
        <button
          className="input-stop"
          type="button"
          onClick={onStop}
        >
          Stop assessment
        </button>
      ) : (
        <button
          className="input-submit"
          type="button"
          onClick={onReset}
        >
          New assessment
        </button>
      )}
    </div>
  );
}

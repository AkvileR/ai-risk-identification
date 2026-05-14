import React, { useState } from "react";
import { useStream } from "@langchain/langgraph-sdk/react";
import "./App.css";
import { API_URL, ASSISTANT_ID } from "./api/graphClient";
import { AppState, ClarificationPayload } from "./types";
import { InputView, InputPhase } from "./views/InputView";
import { ClarificationModal } from "./views/ClarificationModal";
import { VerdictView } from "./views/VerdictView";
import { RunningView } from "./views/RunningView";

function App() {
  const stream = useStream<
    AppState,
    { InterruptType: ClarificationPayload }
  >({
    apiUrl: API_URL,
    assistantId: ASSISTANT_ID,
  });

  const [userStopped, setUserStopped] = useState(false);
  const [submittedText, setSubmittedText] = useState<string | null>(null);

  const verdict = stream.values?.verdict;
  const interrupt = stream.interrupt;
  const findings = stream.values?.criterion_findings ?? {};
  const activePhase = stream.values?.active_phase ?? "";
  const systemDescription = stream.values?.system_description ?? null;
  const hasActivity =
    stream.isLoading ||
    Object.keys(findings).length > 0 ||
    !!systemDescription;

  const phase: InputPhase = userStopped
    ? "stopped"
    : stream.isLoading || interrupt
      ? "running"
      : hasActivity || stream.error
        ? "stopped"
        : "idle";

  const handleSubmit = (userInput: string) => {
    setUserStopped(false);
    setSubmittedText(userInput);
    stream.submit({ user_input: userInput });
  };

  const handleClarification = (answers: Record<string, string>) => {
    stream.submit(undefined, { command: { resume: answers } });
  };

  const handleStop = async () => {
    await stream.stop();
    setUserStopped(true);
  };

  const handleReset = () => {
    setUserStopped(false);
    setSubmittedText(null);
    stream.switchThread(null);
  };

  if (verdict) {
    return (
      <div className="app">
        <VerdictView verdict={verdict} onReset={handleReset} />
      </div>
    );
  }

  const showModal =
    !!interrupt && interrupt.value != null && phase === "running";

  return (
    <div className="app">
      <InputView
        phase={phase}
        submittedText={submittedText}
        onSubmit={handleSubmit}
        onStop={handleStop}
        onReset={handleReset}
      />

      {hasActivity && (
        <RunningView
          findings={findings}
          activePhase={activePhase}
          systemDescription={systemDescription}
          isLoading={stream.isLoading}
          isWaitingForUser={!!interrupt}
        />
      )}

      {stream.error != null && <ErrorBanner error={stream.error} />}

      {showModal && (
        <ClarificationModal
          payload={interrupt!.value as ClarificationPayload}
          onAnswer={handleClarification}
          onClose={handleStop}
        />
      )}
    </div>
  );
}

function extractErrorMessage(error: unknown): string {
  if (error == null) return "";
  if (error instanceof Error) return error.message;
  if (typeof error === "string") return error;
  if (typeof error === "object") {
    const maybe = error as { message?: unknown; error?: unknown };
    if (typeof maybe.message === "string") return maybe.message;
    if (typeof maybe.error === "string") return maybe.error;
    try {
      return JSON.stringify(error);
    } catch {
      return String(error);
    }
  }
  return String(error);
}

function isResourceExhausted(message: string): boolean {
  const m = message.toUpperCase();
  return (
    m.includes("[RESOURCE_EXHAUSTED]") ||
    m.includes("RESOURCE_EXHAUSTED") ||
    m.includes("429") ||
    m.includes("QUOTA")
  );
}

function ErrorBanner({ error }: { error: unknown }) {
  const message = extractErrorMessage(error);
  if (isResourceExhausted(message)) {
    return (
      <div className="error-banner error-quota">
        <strong>API quota reached.</strong> Gemini returned a
        RESOURCE_EXHAUSTED response. Wait a moment and try again — your daily
        or per-minute quota has been hit.
        <div className="error-detail">{message}</div>
      </div>
    );
  }
  return (
    <div className="error-banner">
      <strong>Error:</strong> {message}
    </div>
  );
}

export default App;

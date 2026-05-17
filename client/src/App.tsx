import React, { useEffect, useState } from "react";
import { useStream } from "@langchain/langgraph-sdk/react";
import "./App.css";
import { API_URL, ASSISTANT_ID, buildAuthHeaders } from "./api/graphClient";
import { AppState, ClarificationPayload } from "./types";
import { InputView, InputPhase } from "./views/InputView";
import { ClarificationModal } from "./views/ClarificationModal";
import { VerdictView } from "./views/VerdictView";
import { RunningView } from "./views/RunningView";
import { AccessCredentials } from "./views/AccessGate";

interface AppProps {
  credentials: AccessCredentials;
}

function App({ credentials }: AppProps) {
  const stream = useStream<
    AppState,
    { InterruptType: ClarificationPayload }
  >({
    apiUrl: API_URL,
    assistantId: ASSISTANT_ID,
    defaultHeaders: buildAuthHeaders(credentials.passcode, credentials.email),
  });

  const [userStopped, setUserStopped] = useState(false);
  const [submittedText, setSubmittedText] = useState<string | null>(null);
  const [modalDismissed, setModalDismissed] = useState(false);
  const [clarificationIndex, setClarificationIndex] = useState(0);
  const [clarificationAnswers, setClarificationAnswers] = useState<
    Record<string, string>
  >({});

  const verdict = stream.values?.verdict;
  const interrupt = stream.interrupt;
  const clarificationPayload =
    interrupt && interrupt.value != null
      ? (interrupt.value as ClarificationPayload)
      : null;
  const interruptKey = clarificationPayload
    ? clarificationPayload.questions.map((q) => q.criterion_id).join("|")
    : null;
  const findings = stream.values?.criterion_findings ?? {};
  const activePhase = stream.values?.active_phase ?? "";
  const systemDescription = stream.values?.system_description ?? null;
  const hasActivity =
    stream.isLoading ||
    Object.keys(findings).length > 0 ||
    !!systemDescription;

  useEffect(() => {
    if (interruptKey) {
      setClarificationIndex(0);
      setClarificationAnswers({});
      setModalDismissed(false);
    }
  }, [interruptKey]);

  const phase: InputPhase = userStopped
    ? "stopped"
    : stream.isLoading || interrupt
      ? "running"
      : hasActivity || stream.error
        ? "stopped"
        : "idle";

  const runMetadata = { user_email: credentials.email };

  const handleSubmit = (userInput: string) => {
    setUserStopped(false);
    setSubmittedText(userInput);
    stream.submit({ user_input: userInput }, { metadata: runMetadata });
  };

  const handleClarification = (answers: Record<string, string>) => {
    stream.submit(undefined, {
      command: { resume: answers },
      metadata: runMetadata,
    });
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
        <VerdictView
          verdict={verdict}
          findings={findings}
          onReset={handleReset}
        />
      </div>
    );
  }

  const showModal =
    !modalDismissed && !!clarificationPayload && phase === "running";

  const onResumeClarification =
    modalDismissed && clarificationPayload && phase === "running"
      ? () => setModalDismissed(false)
      : null;

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
          onResumeClarification={onResumeClarification}
        />
      )}

      {stream.error != null && <ErrorBanner error={stream.error} />}

      {showModal && (
        <ClarificationModal
          payload={clarificationPayload!}
          index={clarificationIndex}
          answers={clarificationAnswers}
          onIndexChange={setClarificationIndex}
          onAnswersChange={setClarificationAnswers}
          onAnswer={handleClarification}
          onClose={() => setModalDismissed(true)}
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

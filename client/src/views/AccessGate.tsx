import React, { useState } from "react";
import { API_URL, buildAuthHeaders } from "../api/graphClient";

export interface AccessCredentials {
  email: string;
  passcode: string;
}

interface Props {
  onUnlock: (credentials: AccessCredentials) => void;
}

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

async function verifyCredentials(
  email: string,
  passcode: string,
): Promise<string | null> {
  try {
    const res = await fetch(`${API_URL}/assistants/search`, {
      method: "POST",
      headers: {
        ...buildAuthHeaders(passcode, email),
        "content-type": "application/json",
      },
      body: JSON.stringify({ limit: 1 }),
    });
    if (res.ok) return null;
    if (res.status === 401) return "Incorrect passcode.";
    if (res.status === 500) {
      return "Server isn't fully configured. Ask the admin to set APP_PASSCODE.";
    }
    return `Could not verify (HTTP ${res.status}). Try again.`;
  } catch {
    return "Cannot reach the server. Check the API URL.";
  }
}

export function AccessGate({ onUnlock }: Props) {
  const [email, setEmail] = useState("");
  const [passcode, setPasscode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [verifying, setVerifying] = useState(false);

  const trimmedEmail = email.trim();
  const trimmedPasscode = passcode.trim();
  const emailValid = EMAIL_PATTERN.test(trimmedEmail);
  const canSubmit =
    emailValid && trimmedPasscode.length > 0 && !verifying;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    setVerifying(true);
    setError(null);
    const failure = await verifyCredentials(trimmedEmail, trimmedPasscode);
    setVerifying(false);
    if (failure) {
      setError(failure);
      return;
    }
    onUnlock({ email: trimmedEmail, passcode: trimmedPasscode });
  };

  return (
    <form className="input-view" onSubmit={handleSubmit}>
      <h1>EU AI Act Risk Identification</h1>
      <p className="input-hint">
        This tool is access-restricted. Enter your email and passcode to continue.
      </p>
      <input
        type="email"
        className="input-textarea"
        style={{ height: "auto" }}
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="you@example.com"
        autoComplete="email"
      />
      <input
        type="password"
        className="input-textarea"
        style={{ height: "auto", marginTop: "0.75rem" }}
        value={passcode}
        onChange={(e) => setPasscode(e.target.value)}
        placeholder="Passcode"
        autoComplete="current-password"
      />
      {error && (
        <div
          className="error-banner"
          style={{ marginTop: "0.75rem" }}
        >
          {error}
        </div>
      )}
      <div className="input-footer">
        <span className="char-counter">
          {emailValid ? "" : "Enter a valid email"}
        </span>
        <button
          className="input-submit"
          type="submit"
          disabled={!canSubmit}
        >
          {verifying ? "Verifying…" : "Continue"}
        </button>
      </div>
    </form>
  );
}

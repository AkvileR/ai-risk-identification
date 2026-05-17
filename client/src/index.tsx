import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import { AccessGate, AccessCredentials } from "./views/AccessGate";

const STORAGE_KEY = "risk-agent-access";

function loadStoredCredentials(): AccessCredentials | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (typeof parsed?.email === "string" && typeof parsed?.passcode === "string") {
      return parsed;
    }
  } catch {
    return null;
  }
  return null;
}

function Root() {
  const [credentials, setCredentials] = useState<AccessCredentials | null>(
    loadStoredCredentials,
  );

  useEffect(() => {
    if (credentials) {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(credentials));
    } else {
      sessionStorage.removeItem(STORAGE_KEY);
    }
  }, [credentials]);

  if (!credentials) {
    return (
      <div className="app">
        <AccessGate onUnlock={setCredentials} />
      </div>
    );
  }

  return <App credentials={credentials} />;
}

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement,
);
root.render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>,
);

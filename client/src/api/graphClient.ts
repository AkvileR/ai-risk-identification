export const ASSISTANT_ID = "risk_agent";

function resolveApiUrl(): string {
  const url = process.env.REACT_APP_LANGGRAPH_API_URL;
  if (url) return url;
  if (process.env.NODE_ENV === "production") {
    throw new Error("REACT_APP_LANGGRAPH_API_URL must be set in production");
  }
  return "http://localhost:2024";
}

export const API_URL = resolveApiUrl();

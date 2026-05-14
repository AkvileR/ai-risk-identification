# EU AI Act Risk Identification — Client

React client for the LangGraph risk identification system (see `../server`).
Streams progress and clarification prompts from the system and renders the final verdict.

## Scripts

- `yarn start` — dev server at http://localhost:3000
- `yarn build` — production build
- `yarn test` — Jest + React Testing Library

## Configuration

Set `REACT_APP_LANGGRAPH_API_URL` to point at the LangGraph server (default `http://localhost:2024`). Used by `src/api/graphClient.ts`.

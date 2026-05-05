# Unit 1: UI Foundation — Tech Stack Decisions

## Backend

| Component | Choice | Version | Rationale |
|---|---|---|---|
| Language | Python | 3.11+ | Required by user; best ecosystem for AI/voice libs |
| Web Framework | FastAPI | 0.111+ | Async-native, built-in WebSocket support, auto OpenAPI docs |
| ASGI Server | Uvicorn | 0.29+ | Standard FastAPI server; supports WebSocket |
| WebSocket | FastAPI WebSocket | (built-in) | Native FastAPI support, no extra library needed |
| CORS | FastAPI CORSMiddleware | (built-in) | Simple CORS config for dev/prod |
| Config | Python dataclasses + json | (stdlib) | Lightweight, no extra dependency |
| Data init | Python pathlib + json | (stdlib) | Create dirs and JSON files without extra libs |

## Frontend

| Component | Choice | Version | Rationale |
|---|---|---|---|
| Framework | React | 18+ | User-specified |
| Language | TypeScript | 5+ | User-specified; type safety for WS messages |
| Build Tool | Vite | 5+ | Fast HMR, simple config, standard for React+TS |
| Styling | CSS Modules or Tailwind CSS | latest | Tailwind preferred for rapid dark-theme UI |
| State Management | React Context + useState | (built-in) | Sufficient for single-user app; no Redux needed |
| WebSocket | Browser native WebSocket API | (built-in) | No library needed for basic WS |
| Icons | Lucide React | latest | Lightweight, consistent icon set |

## Development Tools

| Tool | Purpose |
|---|---|
| `requirements.txt` | Python dependency pinning |
| `package.json` | Node dependency management |
| `tsconfig.json` | TypeScript strict mode configuration |
| `vite.config.ts` | Vite dev server proxy (forward `/ws` to FastAPI) |

## Vite Proxy Configuration (Development)
```typescript
// vite.config.ts
server: {
  proxy: {
    '/ws': { target: 'ws://localhost:8000', ws: true },
    '/api': { target: 'http://localhost:8000' }
  }
}
```
This allows the React dev server (port 5173) to proxy WebSocket and API calls to FastAPI (port 8000) during development — no CORS issues.

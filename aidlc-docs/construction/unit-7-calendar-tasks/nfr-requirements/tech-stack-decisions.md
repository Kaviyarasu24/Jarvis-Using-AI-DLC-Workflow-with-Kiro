# Unit 7: Calendar & Tasks — Tech Stack Decisions

| Component | Choice | Rationale |
|---|---|---|
| Storage | Local JSON file (`data/tasks.json`) | User-specified; simple; no database dependency |
| Date handling | Python `datetime` (stdlib) | Sufficient for date parsing and comparison |
| REST framework | FastAPI (existing) | Already in use; add new routes to existing app |
| Frontend data fetching | `fetch` API (browser native) | No extra library needed for simple REST calls |

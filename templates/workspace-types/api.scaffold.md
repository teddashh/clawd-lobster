# API Service Scaffold

## Directory Structure

```
<workspace>/
├── CLAUDE.md
├── workspace.json
├── .gitignore
├── .dockerignore
├── knowledge/
├── skills/learned/
├── openspec/
│   ├── project.md
│   ├── changes/
│   └── specs/
├── src/
│   ├── routes/              # API endpoints
│   ├── models/              # Data models
│   ├── services/            # Business logic
│   ├── middleware/           # Auth, validation, logging
│   └── utils/               # Shared helpers
├── tests/
│   ├── unit/
│   ├── integration/
│   └── api/                 # API endpoint tests
├── deploy/
│   ├── infra-spec.md
│   ├── Dockerfile
│   ├── docker-compose.dev.yml
│   ├── docker-compose.staging.yml
│   ├── docker-compose.prod.yml
│   ├── .env.example
│   └── scripts/
│       ├── deploy-staging.sh
│       └── deploy-prod.sh
└── docs/
    └── api.md               # API documentation
```

## Notes

- No frontend — API only. If a frontend is needed later, upgrade to `webapp` type.
- API docs can be auto-generated (OpenAPI/Swagger) or manual.
- `tests/api/` contains endpoint-level tests (HTTP request/response).

# Deploy — Docker Deployment Pipeline

Ship your projects to dev/staging/prod with one command.

## What It Does

The deploy skill auto-detects your tech stack and generates Docker deployment configs. It reads `workspace.json` to understand your project type, then creates Dockerfiles, docker-compose files, nginx configs, and deploy scripts for three environments.

**Three environments, one philosophy:**
- **Dev** — Playground. Break things freely. Hot reload. `localhost`.
- **Staging** — Verify. Manual Claude OK. Mirror of prod.
- **Prod** — Sacred. Git push + CI/CD only. No direct Claude access.

## How to Use

```bash
/deploy              # Initialize deployment pipeline
/deploy:init         # Same as above
/deploy:build        # Generate Docker configs for detected stack
/deploy:ship dev     # Deploy to dev environment
/deploy:ship staging # Deploy to staging
/deploy:status       # Show deployment state across environments
/deploy:teardown dev # Tear down an environment
```

Triggers on: `/deploy`, 'ship this', 'deploy to staging', 'containerize'.

## Stack Detection

Automatically detects your stack from project files:

| Signal | Stack |
|--------|-------|
| `package.json` | Node.js |
| `requirements.txt` / `pyproject.toml` | Python |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `composer.json` | PHP |
| `Gemfile` | Ruby |
| `*.csproj` / `*.sln` | .NET |

## Generated Files

```
deploy/
  Dockerfile                    # Multi-stage, non-root user
  docker-compose.dev.yml        # Dev with hot reload
  docker-compose.staging.yml    # Staging with SSL
  docker-compose.prod.yml       # Prod with health checks
  nginx/
    dev.conf                    # Dev reverse proxy
    staging.conf                # Staging with SSL termination
    prod.conf                   # Prod with caching
  scripts/
    deploy-staging.sh           # One-command staging deploy
    deploy-prod.sh              # One-command prod deploy
  .env.example                  # Template (never committed)
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `default_cloud` | string | `"none"` | Cloud provider (gcp/aws/azure/self-hosted/none) |
| `auto_ssl` | boolean | `true` | Auto-configure Let's Encrypt SSL |
| `docker_compose_version` | string | `"3.8"` | Docker Compose file version |

## Setup

Docker is optional but recommended. The skill works without it (generates configs only).

## Architecture

Depends on the **spec** skill — reads `workspace.json` created during `/spec` workspace setup. Uses `openspec/changes/v1/design.md` for stack and architecture info.

# Deploy — Workspace-Aware Deployment Pipeline

Ship any workspace to dev/staging/prod with Docker containerization.
This skill reads `workspace.json` to understand the project type, tech stack,
and deployment targets — then generates or executes the appropriate pipeline.

**Philosophy:** Dev = playground (break things freely). Staging = verify (manual Claude OK).
Prod = sacred (git push + CI/CD only, no Claude). Three environments, one source of truth.

---

## CRITICAL: This Skill Reads workspace.json

Every `/deploy` command starts by reading `workspace.json` in the current workspace root.
If it doesn't exist, guide the user to run `/spec` first (which creates it during workspace setup).

```json
{
  "name": "my-saas",
  "type": "webapp",
  "created": "2026-04-08",
  "stack": {
    "runtime": "python",
    "framework": "fastapi",
    "db": "postgresql",
    "cache": "redis",
    "web_server": "nginx"
  },
  "deploy": {
    "dev":     { "mode": "local", "port": 8000 },
    "staging": { "host": "", "method": "docker-compose", "ssh_user": "" },
    "prod":    { "host": "", "method": "ci-cd", "ssh_user": "" }
  },
  "ship_ready": false
}
```

---

## Modes

| Invocation | Mode | Description |
|-----------|------|-------------|
| `/deploy` or `/deploy:init` | **Init** | Detect stack, ask targets, write workspace.json deploy section + infra spec |
| `/deploy:build` | **Build** | Generate Docker configs for all configured environments |
| `/deploy:ship <env>` | **Ship** | Deploy to a specific environment (dev/staging/prod) |
| `/deploy:status` | **Status** | Show deployment state across all environments |
| `/deploy:teardown <env>` | **Teardown** | Tear down a specific environment's containers |

---

## Mode 1: `/deploy` or `/deploy:init` — Initialize Deploy Pipeline

Three steps: detect, ask, write.

### Step 1: Detect Tech Stack

Scan the workspace root for stack indicators. Be thorough — check multiple signals:

| Signal | Detects |
|--------|---------|
| `package.json` | Node.js — check `dependencies` for framework (express, fastapi, next, nuxt, etc.) |
| `requirements.txt` / `pyproject.toml` / `Pipfile` | Python — check for django, flask, fastapi |
| `composer.json` | PHP — check for laravel, symfony |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `Gemfile` | Ruby — check for rails |
| `*.csproj` / `*.sln` | .NET |
| `docker-compose*.yml` | Already has Docker (offer to extend, not overwrite) |
| `Dockerfile` | Already has Docker (offer to extend, not overwrite) |
| `openspec/` | Has specs — read design.md for stack info |

If detection finds existing Docker configs, ask:
"You already have Docker configs. Want me to extend them with multi-environment support, or start fresh?"

### Step 2: Ask Deployment Targets (one round, not a quiz)

Ask ONE consolidated question:

```
I detected your stack: [Python/FastAPI + PostgreSQL + Redis]

Where do you want to deploy?
1. Just local dev (Docker on this machine)
2. Local dev + cloud staging (I'll need the staging server IP)
3. Full pipeline: dev + staging + prod (I'll need both server IPs)
4. I don't know yet — just set up local dev, I'll add servers later

Also: do you have a domain name, or should I use IP-based URLs for now?
```

Adapt the question based on workspace type:
- **webapp/api**: Ask all of the above
- **agent/mcp-server**: Default to local-only, mention cloud is optional
- **skill**: No deploy needed (skills register via `/skill:register`)
- **project**: No deploy needed

### Step 3: Write Configuration

1. **Update `workspace.json`** — fill in the `deploy` section with answers from Step 2.
2. **Generate `deploy/infra-spec.md`** — an OpenSpec-format spec describing the infrastructure:

```markdown
# Infrastructure Spec: <project-name>

## Stack
- Runtime: [detected]
- Framework: [detected]
- Database: [detected]
- Cache: [detected]
- Web Server: nginx (reverse proxy)

## Environments

### Dev (local)
- Port: [chosen or default]
- Database: local container
- Hot reload: enabled
- Debug: enabled

### Staging
- Host: [user-provided or TBD]
- SSL: Let's Encrypt (auto)
- Database: container or managed service
- Resources: minimal (e2-small equivalent)

### Prod
- Host: [user-provided or TBD]
- SSL: Let's Encrypt (auto)
- Database: managed service recommended
- Resources: standard (e2-standard-2+ equivalent)
- Claude Code: NEVER run here

## Security
- Secrets via .env files (gitignored)
- SSH key-based auth only
- Database credentials rotated per environment
- No hardcoded IPs or passwords in committed files
```

3. **Report:**
```
Deploy pipeline initialized:
|- Stack: Python/FastAPI + PostgreSQL + Redis + Nginx
|- Environments: dev (local:8000), staging (TBD), prod (TBD)
|- Infra spec: deploy/infra-spec.md
\- Run /deploy:build to generate Docker configs
```

---

## Mode 2: `/deploy:build` — Generate Docker Configs

Read `workspace.json` and generate Docker configs for each configured environment.

### Output Structure

```
<workspace>/
├── deploy/
│   ├── infra-spec.md          ← from init
│   ├── Dockerfile             ← multi-stage, shared across envs
│   ├── docker-compose.dev.yml
│   ├── docker-compose.staging.yml
│   ├── docker-compose.prod.yml
│   ├── nginx/
│   │   ├── dev.conf
│   │   ├── staging.conf
│   │   └── prod.conf
│   ├── .env.example           ← template, never real secrets
│   └── scripts/
│       ├── deploy-staging.sh
│       └── deploy-prod.sh
├── .env.dev                   ← gitignored
├── .env.staging               ← gitignored
└── .env.prod                  ← gitignored
```

### Dockerfile Rules

1. **Multi-stage build** — builder stage + runtime stage.
2. **Non-root user** — always run as non-root in production.
3. **Health check** — include HEALTHCHECK instruction.
4. **No secrets in image** — all secrets via environment variables.
5. **Pin versions** — use specific image tags, never `latest`.
6. **.dockerignore** — generate one, exclude .git, node_modules, __pycache__, .env*, etc.

### Environment-Specific Differences

| Aspect | Dev | Staging | Prod |
|--------|-----|---------|------|
| **Volumes** | Mount source code (hot reload) | No source mount | No source mount |
| **Ports** | Expose all (debug) | Expose 80/443 only | Expose 80/443 only |
| **Restart** | `no` | `unless-stopped` | `always` |
| **Logging** | Console | JSON file | JSON file + optional log driver |
| **Resources** | No limits | Soft limits | Hard limits |
| **DB** | Local container | Container or managed | Managed recommended |
| **Debug** | Enabled | Disabled | Disabled |
| **SSL** | None | Let's Encrypt | Let's Encrypt |

### Stack-Specific Templates

Generate configs based on detected stack. Common patterns:

**Python/FastAPI:**
```yaml
services:
  app:
    build: .
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    # dev: add --reload
```

**Node.js/Express or Next.js:**
```yaml
services:
  app:
    build: .
    command: node server.js
    # dev: use npm run dev
    # next: npm run build && npm start
```

**PHP/Laravel:**
```yaml
services:
  app:
    build: .
    # php-fpm + nginx combo
  nginx:
    image: nginx:1.25-alpine
```

### Deploy Scripts

Generate `deploy/scripts/deploy-staging.sh` and `deploy-prod.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

ENV="${1:-staging}"
HOST="$(grep DEPLOY_HOST ".env.${ENV}" | cut -d= -f2)"
SSH_USER="$(grep SSH_USER ".env.${ENV}" | cut -d= -f2)"

echo "=== Deploying to ${ENV} (${HOST}) ==="

# Sync project files
rsync -avz --exclude='.git' --exclude='node_modules' \
  --exclude='__pycache__' --exclude='.env*' \
  ./ "${SSH_USER}@${HOST}:~/app/"

# Copy env file
scp ".env.${ENV}" "${SSH_USER}@${HOST}:~/app/.env"

# Build and start on remote
ssh "${SSH_USER}@${HOST}" << 'REMOTE'
  cd ~/app
  docker compose -f "docker-compose.${ENV}.yml" build
  docker compose -f "docker-compose.${ENV}.yml" up -d
  docker compose -f "docker-compose.${ENV}.yml" ps
REMOTE

echo "=== Deploy to ${ENV} complete ==="
```

### After Build

1. **Add `.env*` to `.gitignore`** (if not already there).
2. **Commit deploy configs:** `git add deploy/ .dockerignore .gitignore && git commit -m "Add deploy pipeline"`
3. **Report:**
```
Deploy configs generated:
|- Dockerfile (multi-stage, non-root)
|- 3 docker-compose files (dev/staging/prod)
|- Nginx configs per environment
|- Deploy scripts for staging + prod
|- .env.example (template)
\- Run /deploy:ship dev to start local development
```

---

## Mode 3: `/deploy:ship <env>` — Deploy to Environment

### Ship to Dev (local)

```bash
docker compose -f deploy/docker-compose.dev.yml up --build -d
```

Then report the local URL and service status.

### Ship to Staging

1. **Preflight checks:**
   - `.env.staging` exists and has DEPLOY_HOST
   - SSH connectivity: `ssh -o ConnectTimeout=5 user@host echo ok`
   - Docker is installed on remote: `ssh user@host docker --version`
2. **Execute:** run `deploy/scripts/deploy-staging.sh`
3. **Verify:** check services are healthy via Docker on remote
4. **Report:** staging URL + service status

### Ship to Prod

1. **SAFETY GATE:** Always confirm with user before prod deploy.
   ```
   ⚠️ Production deployment to [host]
   - Branch: main
   - Last commit: [hash] [message]
   - Staging verified: [yes/no]
   
   Proceed? (yes/no)
   ```
2. **Require main branch:** refuse to deploy from feature branches.
3. **Require staging first:** warn if staging hasn't been deployed or verified.
4. **Execute:** prefer CI/CD if configured, otherwise run deploy script.
5. **Verify + report.**

### Ship for Non-Web Types

| Type | Ship Action |
|------|------------|
| **agent** | Register with agent framework, start as service |
| **mcp-server** | Write to `.mcp.json`, restart Claude |
| **skill** | Copy to skills/, register in skill index |
| **project** | No ship — just git push |

---

## Mode 4: `/deploy:status` — Show Deployment State

```
Workspace: my-saas (webapp)
Stack: Python/FastAPI + PostgreSQL + Redis

Environment Status:
  Dev     ✅ Running    localhost:8000    3 containers healthy
  Staging ⚠️ Not deployed  staging.example.com configured
  Prod    ❌ Not configured

Last Deploy:
  Dev:     2026-04-08 14:30 (local)
  Staging: never
  Prod:    never
```

Determine status by:
- **Local:** `docker compose -f deploy/docker-compose.dev.yml ps`
- **Remote:** `ssh user@host docker compose -f docker-compose.staging.yml ps` (if SSH accessible)
- **Not configured:** `workspace.json` deploy section is empty for that env

---

## Mode 5: `/deploy:teardown <env>` — Tear Down Environment

1. **Confirm:** "This will stop and remove all containers for [env]. Proceed?"
2. **Execute:** `docker compose -f deploy/docker-compose.<env>.yml down -v` (include `-v` only if user confirms volume removal)
3. **For remote:** SSH and run the same command
4. **Report:** containers stopped, volumes status

---

## Workspace Type Awareness

This skill adapts its behavior based on `workspace.json` type:

| Type | Docker? | Environments | Ship Method |
|------|---------|-------------|-------------|
| **webapp** | Yes, full stack | dev + staging + prod | docker-compose + deploy scripts |
| **api** | Yes, backend only | dev + staging + prod | docker-compose + deploy scripts |
| **agent** | Optional (single container) | dev only (default) | Register with agent framework |
| **mcp-server** | Optional (single container) | dev only (default) | .mcp.json registration |
| **skill** | No | N/A | skill:register |
| **project** | No | N/A | git push only |

---

## Integration with /spec

The `/spec` skill creates `workspace.json` with a `type` field during Phase 2.
`/deploy` reads that type and adapts. The flow is:

```
/spec          → creates workspace + workspace.json (with type)
/deploy:init   → reads type, detects stack, configures deploy targets
/deploy:build  → generates Docker configs based on type + stack
/deploy:ship   → deploys to target environment
```

If the user runs `/deploy` before `/spec`, create a minimal `workspace.json`
by asking type and stack directly.

---

## Security Rules

1. **Never commit `.env` files** — only `.env.example` with placeholder values.
2. **Never hardcode IPs, passwords, or SSH keys** in any committed file.
3. **Never store Docker registry credentials** in deploy configs.
4. **Prod deploys require explicit confirmation** — no auto-deploy to prod.
5. **No `--dangerously-skip-permissions` in staging/prod** — dev only.
6. **Deploy scripts use `set -euo pipefail`** — fail fast on any error.
7. **All containers run as non-root** in staging and prod.
8. **Health checks are mandatory** for all services.

---

## File Safety

- Deploy configs go inside the workspace, under `deploy/`.
- Never modify files outside the workspace directory.
- Never commit secrets, credentials, or real `.env` files.
- Never include personal names, machine-specific paths, or hardcoded user info.
- All generated scripts must be portable across Linux/macOS/WSL.

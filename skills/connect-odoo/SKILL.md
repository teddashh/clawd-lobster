# Odoo ERP Connector

!python -m connect_odoo.server --health 2>/dev/null || echo "Odoo connection not configured or unreachable"

Connects a Clawd-Lobster agent to an Odoo ERP instance via XML-RPC. Provides MCP tools for searching, reading, creating, and updating records across any Odoo model (CRM, HR, Invoicing, etc.), plus a poller that checks for pending agent tasks.

## Enabling

This skill is **disabled by default**. Enable it in your workspace config:

```jsonc
// workspaces.json — skill overrides
"skills": {
  "connect-odoo": { "enabled": true }
}
```

## Credentials

Before using, configure the `odoo-server` credential with:

| Field      | Description                          | Example                   |
|------------|--------------------------------------|---------------------------|
| `url`      | Odoo instance URL (with port)        | `http://your-odoo:8069`   |
| `db`       | PostgreSQL database name             | `mydb`                    |
| `user`     | Odoo login (usually an email)        | `admin@company.com`       |
| `password` | Odoo user password or API key        | *(stored securely)*       |

Credentials are resolved at runtime via the `${credential:...}` syntax in `skill.json` and passed as environment variables. Never hardcode credentials in source files.

## MCP Tools

Once enabled, the agent gains these tools:

| Tool               | Description                                      |
|--------------------|--------------------------------------------------|
| `odoo_search`      | Search records with domain filters               |
| `odoo_read`        | Read specific records by ID                      |
| `odoo_create`      | Create a new record                              |
| `odoo_write`       | Update existing records                          |
| `odoo_execute`     | Call any Odoo model method                       |
| `odoo_poll_tasks`  | Check for pending tasks assigned to this agent   |

## Poller

The skill includes a poller (`connect_odoo/poller.py`) that runs on a cron schedule (default: every 5 minutes). It queries Odoo for pending `arp.task` records and outputs them as JSON. If the `arp.task` model does not exist on the target Odoo instance, the poller returns an empty list without error.

## Health Check

Test connectivity at any time:

```bash
python -m connect_odoo.server --health
```

Returns JSON with `status: "ok"` and the Odoo server version, or `status: "error"` with details.

## Configuration

Optional settings in `configDefaults`:

- **`poll_interval_seconds`** — How often the poller runs (default: 300).
- **`modules`** — Which Odoo modules to interact with (default: `["crm"]`).
- **`sync_direction`** — `pull`, `push`, or `bidirectional` (default: `bidirectional`).

## Dependencies

- Python 3.11+
- `fastmcp` (for MCP server)
- Python's built-in `xmlrpc.client` (no additional packages needed for Odoo communication)

## Gotchas

1. **Hardcoding business logic in executors.** Odoo already handles workflows, validations, and computed fields natively. Claude tends to re-implement business rules in the executor layer instead of calling the appropriate Odoo model method. Always check if Odoo's built-in automation or server action can do it first.

2. **XML-RPC type coercion surprises.** Odoo's XML-RPC returns `False` (Python bool) instead of `None` for empty relational fields. Claude may treat `False` as a meaningful value. Always check `if result and result != False` for nullable fields.

3. **Domain filter syntax errors.** Odoo domain filters use Polish notation: `['&', ('field', '=', 'val1'), ('field2', '>', 5)]`. Claude often writes SQL-like conditions or forgets the `&`/`|` prefix operators for compound filters. Triple-check domain syntax before calling `odoo_search`.

4. **Polling a model that does not exist.** The poller queries `arp.task` by default, which is a custom module. On vanilla Odoo instances this model does not exist. The poller handles this gracefully (returns empty list), but Claude may report "no tasks found" without mentioning the model is missing — always distinguish "no tasks" from "model not found".

5. **Credential environment variables not set.** The MCP server reads `ODOO_URL`, `ODOO_DB`, `ODOO_USER`, `ODOO_PASSWORD` from environment. If credentials are not configured via the credential store, the server starts but every call fails with a cryptic XML-RPC fault. Always verify credentials are set before diagnosing connection issues.

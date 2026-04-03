# Odoo ERP Connector

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

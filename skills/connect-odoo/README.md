# Odoo ERP Connector

> XML-RPC connection to Odoo for CRM, HR, and invoicing automation.

## What It Does

Connect-Odoo bridges clawd-lobster to an Odoo ERP instance via XML-RPC,
exposing standard CRUD operations as MCP tools. A built-in poller watches for
pending `arp.task` records so the agent can pick up work assigned through the
Odoo ARP module automatically.

## How It Works

The skill registers six MCP tools:

| Tool | Description |
|------|-------------|
| `odoo_search` | Search records by domain filter |
| `odoo_read` | Read fields from specific record IDs |
| `odoo_create` | Create new records in any model |
| `odoo_write` | Update existing records |
| `odoo_execute` | Call arbitrary Odoo model methods |
| `odoo_poll_tasks` | Check for pending `arp.task` records |

The poller runs on a configurable interval (default 5 minutes) and picks up
tasks assigned to the agent in Odoo's ARP task queue.

## Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `poll_interval_seconds` | integer | `300` | Polling interval in seconds (minimum 60) |
| `modules` | array | `["crm"]` | Odoo modules to enable |
| `sync_direction` | string | | Direction of data sync |

## Dependencies

- `memory-server` skill
- `python >= 3.11`

## Credentials

| Credential | Fields | Description |
|------------|--------|-------------|
| `odoo-server` | `url`, `db`, `user`, `password` | Odoo instance connection details |

## Health Check

`python -m connect_odoo.server --health` is executed every 600 seconds to
verify the XML-RPC connection is alive.

## Maintenance

The connector uses Odoo's stable XML-RPC interface, which rarely changes
between versions. When upgrading Odoo, verify that the target modules still
exist and field names have not changed. The poller respects the minimum interval
of 60 seconds to avoid overloading the Odoo server.

---

**Version:** 0.1.0 | **Kind:** poller | **Default:** disabled (optional)

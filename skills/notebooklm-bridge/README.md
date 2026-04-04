# NotebookLM Bridge

> Auto-connect workspaces to Google NotebookLM for free RAG and content generation.

## What It Does

NotebookLM Bridge syncs workspace documents into Google NotebookLM notebooks,
giving the agent access to free RAG retrieval and multi-format content
generation. After a blitz run, workspace docs are automatically pushed to
NotebookLM so the knowledge stays current.

## How It Works

The skill follows a 3-stage pipeline:

1. **Discovery** -- scan workspace for relevant source documents
2. **Synthesis note** -- generate a structured summary note for NotebookLM
3. **Controlled generation** -- produce outputs using the 8 rules of
   NotebookLM prompting (derived from the AI 3-way debate methodology)

Supported content types:

- Slides
- Infographics
- Podcasts
- Mind-maps
- Quizzes
- Reports

After a spec blitz completes, the bridge auto-syncs updated workspace docs into
the linked notebook.

## Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `auto_sync_sources` | boolean | `false` | Auto-sync docs after blitz |
| `default_language` | string | `zh_Hant` | Default output language |
| `auto_create_notebook` | boolean | `false` | Auto-create notebook if none exists |

## Dependencies

- `memory-server` skill
- `python >= 3.10`
- `notebooklm-py` (unofficial Python API)

## Credentials

| Credential | Fields | Description |
|------------|--------|-------------|
| `google-notebooklm` | `auth_status`, account email | Google account with NotebookLM access |

## Health Check

`python -m notebooklm auth check` is executed every 3600 seconds to verify
authentication status.

## Maintenance

`notebooklm-py` is an **unofficial API wrapper** and comes with caveats:

- **Auth expiry** -- Google OAuth tokens may expire or be revoked. Re-run auth
  flow if the health check starts failing.
- **Rate limits** -- Google applies undocumented rate limits. Space out bulk
  generation requests.
- **Breaking changes** -- The underlying NotebookLM API is not versioned.
  Pin `notebooklm-py` to a known-good version and test before upgrading.
- **Watermark position** -- If NotebookLM changes their watermark location,
  update the `LOGO_COORDS` constant in `remove_watermark.py`.

## Watermark Removal

Built-in tool to remove the NotebookLM logo from generated slides and infographics.

- **No AI / No GPU** -- uses biharmonic inpainting (classical image processing)
- **Auto mode** -- enabled by default (`auto_remove_watermark: true`)
- **Manual**: `python skills/notebooklm-bridge/remove_watermark.py input.pdf`
- **Formats**: PDF (default), `--pptx` (PowerPoint), `--png` (ZIP of images)

Based on [WaterMarkLM](https://huggingface.co/spaces/dseditor/WaterMarkLM) (MIT).

---

**Version:** 0.2.0 | **Kind:** prompt-pattern | **Default:** disabled (optional)

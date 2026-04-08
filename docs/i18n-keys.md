# i18n Key Inventory — Onboarding Redesign

All keys must exist in 5 languages: en, zh-TW, zh-CN, ja, ko.
Shell commands (pip install, npm install, etc.) are NOT translated.

## Page 1: Welcome + Language (8 keys)

| Key | EN | Notes |
|-----|-----|-------|
| `welcome_title` | Welcome to Clawd-Lobster | Hero title |
| `welcome_subtitle` | Let's get started. Please select your language. | Below taglines |
| `welcome_tagline` | You'll end up using Claude Code anyway — why not start with the best experience? | Shown in all 5 langs simultaneously on page, but also used as localized subtitle |
| `lang_title` | Language | Step heading (current, keep) |
| `lang_desc` | Choose your preferred language. | Step description (current, keep) |
| `next` | Next | Shared button |
| `back` | Back | Shared button |
| `welcome_no_python` | Don't have Python yet? Run this first: | Pre-bootstrap notice |

## Page 2: Prerequisites + Claude Code Setup (38 keys)

### Section titles (4 keys)

| Key | EN |
|-----|-----|
| `prereq_title` | System Check |
| `prereq_desc` | Let's make sure everything is ready. |
| `prereq_recheck` | Re-check |
| `prereq_all_ok` | All prerequisites met! |

### Per-prerequisite purpose (6 keys)

| Key | EN |
|-----|-----|
| `prereq_python_purpose` | Runs the memory server and skills |
| `prereq_node_purpose` | Required for Claude Code installation |
| `prereq_git_purpose` | Syncs knowledge across machines |
| `prereq_pip_purpose` | Python package manager |
| `prereq_claude_purpose` | The AI coding assistant |
| `prereq_auth_purpose` | Claude Code authentication |

### Status labels (4 keys)

| Key | EN |
|-----|-----|
| `prereq_checking` | Checking... |
| `prereq_ok` | OK |
| `prereq_missing` | Missing |
| `prereq_optional` | Optional |

### Install guide headers (6 keys)

| Key | EN |
|-----|-----|
| `prereq_python_install` | How to install Python |
| `prereq_node_install` | How to install Node.js |
| `prereq_git_install` | How to install Git |
| `prereq_pip_install` | How to install pip |
| `prereq_claude_install` | How to install Claude Code |
| `prereq_auth_install` | How to authenticate Claude Code |

### Install guide descriptions (6 keys, platform-generic wrapper)

| Key | EN |
|-----|-----|
| `prereq_python_guide` | Download from python.org. Make sure to check "Add to PATH" during installation. |
| `prereq_node_guide` | Download from nodejs.org. LTS version recommended. |
| `prereq_git_guide` | Download from git-scm.com. Use default settings. |
| `prereq_pip_guide` | Usually included with Python. If missing, run: |
| `prereq_claude_guide` | Run in your terminal: |
| `prereq_auth_guide` | Run in your terminal. This will open your browser to log in: |

### Platform tab labels (3 keys)

| Key | EN |
|-----|-----|
| `platform_windows` | Windows |
| `platform_macos` | macOS |
| `platform_linux` | Linux |

### Install detail per platform (9 keys — platform-specific instructions)

| Key | EN |
|-----|-----|
| `prereq_python_win` | Download the installer from python.org/downloads and run it. Check "Add Python to PATH". |
| `prereq_python_mac` | Run: brew install python@3.12 — or download from python.org |
| `prereq_python_linux` | Run: sudo apt install python3 python3-pip — or sudo dnf install python3 |
| `prereq_node_win` | Download the LTS installer from nodejs.org and run it. |
| `prereq_node_mac` | Run: brew install node |
| `prereq_node_linux` | Run: sudo apt install nodejs npm — or use nvm |
| `prereq_git_win` | Download from git-scm.com and run the installer. |
| `prereq_git_mac` | Run: brew install git — or install Xcode Command Line Tools |
| `prereq_git_linux` | Run: sudo apt install git |

## Page 3: Handoff to CLI (14 keys)

| Key | EN |
|-----|-----|
| `handoff_title` | Let Claude Code take it from here |
| `handoff_desc` | Open a terminal and run the command below. Claude Code will guide you through the rest. |
| `handoff_hint` | Or copy and paste this command: |
| `handoff_copy` | Copy command |
| `handoff_copied` | Copied! |
| `handoff_status` | Setup Progress |
| `handoff_persona` | Persona selection |
| `handoff_workspace_root` | Workspace root directory |
| `handoff_workspace` | First workspace |
| `handoff_config` | Configuration |
| `handoff_waiting` | Waiting... |
| `handoff_done` | Done |
| `handoff_manual` | I want to do it manually in the browser instead |
| `handoff_timeout` | Taking a while? Try the manual setup above. |

## Completion Screen (4 keys)

| Key | EN |
|-----|-----|
| `ready` | Ready! | (existing) |
| `ready_desc` | Your workspace has been created. | (existing) |
| `view_ws` | View Workspaces | (existing) |
| `launch_squad` | Launch Spec Squad | (existing) |

## Fallback (manual browser setup, reuses existing keys) (6 keys)

| Key | EN |
|-----|-----|
| `persona_title` | How do you work? | (existing) |
| `persona_desc` | This helps us tailor the experience. | (existing) |
| `persona_guided` | Guided | (existing) |
| `persona_expert` | Expert | (existing) |
| `persona_tech` | Technical | (existing) |
| `ws_title` | Create Your First Workspace | (existing) |
| `ws_name_label` | Workspace name (kebab-case) | (existing) |
| `ws_root_label` | Workspace root directory | (existing) |
| `finish` | Finish Setup | (existing) |
| `finishing` | Setting up... | (existing) |

---

## Total: ~80 keys per language

- Page 1: 8 keys
- Page 2: 38 keys
- Page 3: 14 keys
- Completion: 4 keys (existing)
- Fallback: ~10 keys (existing)
- Shared: 2 keys (back/next, existing)

### Existing keys to keep: ~20 (from current I18N dict)
### New keys to add: ~60 per language
### Total translations needed: 60 new keys × 4 non-EN languages = 240 translations

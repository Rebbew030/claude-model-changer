# claude-model-change

Manage Claude Code **env profiles** — quickly switch between different sets of environment variables in `~/.claude/settings.json`.

Each **profile** is a complete snapshot of the `"env"` section. You can create, edit, delete, and apply profiles with a single command.

## Quick Start

```bash
# One-line install
curl -sSL https://raw.githubusercontent.com/YOUR_USER/claude-model-changer/main/install.sh | bash

# Or clone and run locally
git clone https://github.com/YOUR_USER/claude-model-changer.git
cd claude-model-changer
./install.sh
```

After install, open a new terminal and run:

```bash
claude-model-change
```

## What It Does

This tool **only** touches `settings.json["env"]` — all other settings (`model`, `permissions`, `theme`, `plugins`, etc.) are **never modified**.

| Operation | Description |
|-----------|-------------|
| **Create** | Save your current env as a new named profile |
| **Edit** | Modify an existing profile's values |
| **Delete** | Remove a profile |
| **List** | Show all saved profiles |
| **Change (Apply)** | Replace `settings.json["env"]` with a chosen profile |

Every `change` operation automatically creates a backup of your current env before applying.

## Usage

### Interactive Menu

```bash
claude-model-change
```

```
==================================================
    Claude Code Model Env Profile Manager
==================================================
    Current profile : deepseek-pro
    Saved profiles  : 3
--------------------------------------------------
    1. 📋  List profiles
    2. 🔄  Change (apply) profile
    3. ✨  Create new profile
    4. ✏️   Edit a profile
    5. 🗑️   Delete a profile
    6. 🚪  Exit
--------------------------------------------------
    Choice [1-6]:
```

### Subcommands

```bash
claude-model-change list                # List all profiles
claude-model-change change deepseek-pro # Apply a profile directly
claude-model-change create my-profile   # Create new profile interactively
claude-model-change edit my-profile     # Edit a profile interactively
claude-model-change delete my-profile   # Delete a profile
```

## Profile Structure

Profiles are stored as JSON files in `profiles/`. Each file matches the structure of `settings.json["env"]`:

```json
{
  "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
  "ANTHROPIC_AUTH_TOKEN": "sk-...",
  "ANTHROPIC_API_KEY": "sk-...",
  "API_TIMEOUT_MS": "3000000",
  "ANTHROPIC_MODEL": "deepseek-v4-pro[1m]",
  "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek-v4-flash",
  "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4-pro[1m]",
  "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-v4-flash",
  "CLAUDE_CODE_SUBAGENT_MODEL": "deepseek-v4-pro[1m]",
  "CLAUDE_CODE_EFFORT_LEVEL": "max",
  "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
  "CLAUDE_CODE_DISABLE_AUTO_UPDATE": "1"
}
```

## Built-in Example Profiles

When you first install, the installer auto-seeds a profile from your current Claude Code settings (if available).

Example profiles are also included for reference (these use placeholder API keys — edit them with your real keys before use):

- `deepseek-pro` — DeepSeek API, pro model, max effort
- `deepseek-flash` — DeepSeek API, flash model, medium effort (faster & cheaper)
- `anthropic-direct` — Direct Anthropic API, claude-sonnet-4-6

## Safety

- **Only `env` is modified** — all other `settings.json` keys are preserved
- **Auto-backup** — before every `change`, current env is saved as `.backup-before-<name>.json`
- **No external dependencies** — uses only Python standard library

## Requirements

- Python 3.9+
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed (`~/.claude/settings.json` must exist)

## Uninstall

```bash
pip3 uninstall claude-model-changer -y
```

## License

MIT

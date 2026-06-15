#!/usr/bin/env bash
set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ── Banner ────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   Claude Code Model Env Profile Manager${NC}"
echo -e "${CYAN}   Installer${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# ── Check: Python 3.9+ ────────────────────────────────────────────
echo -e "→ Checking Python version..."
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}✗ python3 not found. Please install Python 3.9+.${NC}"
    exit 1
fi

PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 9 ]; }; then
    echo -e "${RED}✗ Python $PY_VERSION found, but 3.9+ is required.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PY_VERSION${NC}"

# ── Check: Claude Code settings.json ──────────────────────────────
echo -e "→ Checking Claude Code settings..."
SETTINGS_FILE="$HOME/.claude/settings.json"

if [ ! -f "$SETTINGS_FILE" ]; then
    echo -e "${YELLOW}⚠  $SETTINGS_FILE not found.${NC}"
    echo -e "${YELLOW}   Claude Code may not be installed yet.${NC}"
    echo -e "${YELLOW}   The tool will still install, but you'll need${NC}"
    echo -e "${YELLOW}   Claude Code to use it.${NC}"
    echo ""
    read -rp "   Continue anyway? [y/N]: " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        echo "   Cancelled."
        exit 0
    fi
else
    echo -e "${GREEN}✓ Found $SETTINGS_FILE${NC}"

    HAS_ENV=$(python3 -c "
import json, os
with open(os.path.expanduser('$SETTINGS_FILE')) as f:
    d = json.load(f)
print('yes' if 'env' in d else 'no')
" 2>/dev/null || echo "no")

    if [ "$HAS_ENV" = "yes" ]; then
        echo -e "${GREEN}✓ 'env' section present${NC}"
    else
        echo -e "${YELLOW}⚠  No 'env' section in settings.json — will be created on first use.${NC}"
    fi
fi

# ── Install package ───────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo ""
echo -e "→ Installing claude-model-changer from: $SCRIPT_DIR"

pip3 install -e "$SCRIPT_DIR" 2>&1 | tail -3

# ── Check PATH ────────────────────────────────────────────────────
PYTHON_BIN_DIR=$(python3 -c "import sysconfig; print(sysconfig.get_path('scripts'))")
if echo "$PATH" | grep -q "$PYTHON_BIN_DIR"; then
    echo -e "${GREEN}✓ $PYTHON_BIN_DIR is in PATH${NC}"
else
    echo -e "${YELLOW}⚠  $PYTHON_BIN_DIR is NOT in PATH.${NC}"

    # Detect shell and add to rc file
    SHELL_RC=""
    if [ -n "${ZSH_VERSION:-}" ] || echo "${SHELL:-}" | grep -q zsh 2>/dev/null; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -n "${BASH_VERSION:-}" ] || echo "${SHELL:-}" | grep -q bash 2>/dev/null; then
        if [ -f "$HOME/.bash_profile" ]; then
            SHELL_RC="$HOME/.bash_profile"
        else
            SHELL_RC="$HOME/.bashrc"
        fi
    fi

    if [ -n "$SHELL_RC" ] && [ -f "$SHELL_RC" ]; then
        echo -e "   Adding to ${YELLOW}$SHELL_RC${NC}..."
        {
            echo ""
            echo "# Added by claude-model-changer installer"
            echo "export PATH=\"$PYTHON_BIN_DIR:\$PATH\""
        } >> "$SHELL_RC"
        echo -e "${GREEN}✓ Added to $SHELL_RC${NC}"
        echo -e "   Run ${CYAN}source $SHELL_RC${NC} or open a new terminal."
    else
        echo -e "${YELLOW}   Could not detect shell rc file. Add this manually:${NC}"
        echo -e "   ${CYAN}export PATH=\"$PYTHON_BIN_DIR:\$PATH\"${NC}"
    fi
fi

# ── Seed initial profile ──────────────────────────────────────────
if [ -f "$SETTINGS_FILE" ] && [ "$HAS_ENV" = "yes" ]; then
    echo ""
    echo -e "→ Seeding initial profile from current Claude Code env..."
    python3 -c "
from claude_model_changer.profile_manager import seed_from_current, write_profile, read_env

# Seed current env
seed_from_current('my-current')

# Create Anthropic direct example
anthropic = {
    'ANTHROPIC_BASE_URL': 'https://api.anthropic.com',
    'ANTHROPIC_AUTH_TOKEN': 'sk-ant-your-key-here',
    'ANTHROPIC_API_KEY': 'sk-ant-your-key-here',
    'API_TIMEOUT_MS': '3000000',
    'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC': '1',
    'ANTHROPIC_MODEL': 'claude-sonnet-4-6',
    'ANTHROPIC_DEFAULT_SONNET_MODEL': 'claude-sonnet-4-6',
    'ANTHROPIC_DEFAULT_OPUS_MODEL': 'claude-opus-4-8',
    'ANTHROPIC_DEFAULT_HAIKU_MODEL': 'claude-haiku-4-5-20251001',
    'CLAUDE_CODE_SUBAGENT_MODEL': 'claude-sonnet-4-6',
    'CLAUDE_CODE_EFFORT_LEVEL': 'high',
    'CLAUDE_CODE_DISABLE_AUTO_UPDATE': '1',
}
write_profile('anthropic-direct', anthropic)

# DeepSeek flash (fast/cheap variant of current)
flash = read_env()
flash['ANTHROPIC_MODEL'] = 'deepseek-v4-flash'
flash['ANTHROPIC_DEFAULT_SONNET_MODEL'] = 'deepseek-v4-flash'
flash['ANTHROPIC_DEFAULT_OPUS_MODEL'] = 'deepseek-v4-flash'
flash['ANTHROPIC_DEFAULT_HAIKU_MODEL'] = 'deepseek-v4-flash'
flash['CLAUDE_CODE_SUBAGENT_MODEL'] = 'deepseek-v4-flash'
flash['CLAUDE_CODE_EFFORT_LEVEL'] = 'medium'
write_profile('deepseek-flash', flash)

print('Profiles seeded: my-current, anthropic-direct, deepseek-flash')
" 2>/dev/null && echo -e "${GREEN}✓ Profiles seeded${NC}" || echo -e "${YELLOW}⚠  Could not seed profiles (non-fatal)${NC}"
fi

# ── Done ───────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Install complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "   Run: ${CYAN}claude-model-change${NC}"
echo ""

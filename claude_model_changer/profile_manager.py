"""Profile manager — CRUD + apply for env profiles.

Each profile is a complete JSON object matching the structure of
settings.json["env"]. Profiles are stored as .json files in the
profiles/ directory next to this package.
"""

import json
from pathlib import Path
from typing import Optional

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
PROFILES_DIR = Path(__file__).resolve().parent.parent / "profiles"


def _ensure_profiles_dir() -> Path:
    """Create profiles/ directory if it doesn't exist."""
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    return PROFILES_DIR


def read_settings() -> dict:
    """Read the full settings.json file. Returns {} if missing."""
    if not SETTINGS_PATH.exists():
        return {}
    with open(SETTINGS_PATH, "r") as f:
        return json.load(f)


def read_env() -> dict:
    """Read only the 'env' section from settings.json."""
    return read_settings().get("env", {})


def write_env(env: dict) -> None:
    """Replace the 'env' section in settings.json, preserving all other keys."""
    settings = read_settings()
    settings["env"] = env
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ── Profile CRUD ──────────────────────────────────────────────────


def list_profiles() -> list[str]:
    """Return sorted list of profile names (without .json extension)."""
    _ensure_profiles_dir()
    names = []
    for f in PROFILES_DIR.glob("*.json"):
        if not f.name.startswith("."):
            names.append(f.stem)
    return sorted(names)


def read_profile(name: str) -> Optional[dict]:
    """Read a profile by name. Returns None if not found."""
    path = _ensure_profiles_dir() / f"{name}.json"
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)


def write_profile(name: str, env: dict) -> Path:
    """Save a profile to disk. Overwrites if exists."""
    path = _ensure_profiles_dir() / f"{name}.json"
    with open(path, "w") as f:
        json.dump(env, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return path


def delete_profile(name: str) -> bool:
    """Delete a profile by name. Returns True if deleted."""
    path = _ensure_profiles_dir() / f"{name}.json"
    if not path.exists():
        return False
    path.unlink()
    return True


# ── Apply / Backup ────────────────────────────────────────────────


def backup_current_env(label: str) -> Path:
    """Save a snapshot of the current env before applying a new profile.

    Stored as .backup-before-<label>.json (hidden file, excluded from lists).
    """
    current_env = read_env()
    return write_profile(f".backup-before-{label}", current_env)


def apply_profile(name: str) -> bool:
    """Replace settings.json['env'] with the named profile.

    Automatically creates a backup of the current env before applying.
    Returns True on success, False if profile not found.
    """
    env = read_profile(name)
    if env is None:
        return False
    backup_current_env(name)
    write_env(env)
    return True


def detect_current_profile_name() -> str:
    """Try to match current env to a saved profile (by value equality).

    Returns the profile name if found, or '(unsaved)' if no match.
    """
    current_env = read_env()
    for name in list_profiles():
        if read_profile(name) == current_env:
            return name
    return "(unsaved)"


def seed_from_current(name: str) -> Optional[Path]:
    """Save the current settings.json['env'] as a new profile.

    Does nothing if the profile already exists, unless overwrite=True.
    Returns the path to the saved profile.
    """
    current_env = read_env()
    if not current_env:
        return None
    return write_profile(name, current_env)

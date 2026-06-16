"""CLI — interactive menu and subcommands for claude-model-change."""

import sys
from typing import Optional

from .profile_manager import (
    apply_default,
    apply_profile,
    delete_profile,
    detect_current_profile_name,
    list_profiles,
    read_env,
    read_profile,
    write_profile,
)


# ── Interactive helpers ───────────────────────────────────────────


def _pick_profile(action: str) -> Optional[str]:
    """Show a numbered list of profiles and let the user pick one.

    The "(default)" option (no env vars) is always available at index 0.
    """
    profiles = list_profiles()

    print(f"\n  {action}:")
    print(f"    0. (default)  [no env vars — bare Claude Code]")

    if not profiles:
        print(f"\n  No custom profiles found.\n")
    else:
        for i, name in enumerate(profiles, 1):
            env = read_profile(name)
            model = env.get("ANTHROPIC_MODEL", "?")
            effort = env.get("CLAUDE_CODE_EFFORT_LEVEL", "?")
            count = len(env)
            print(f"    {i}. {name}  [{count} vars]  model={model}  effort={effort}")

    choice = input("\n  Pick a profile (number): ").strip()
    if choice == "0":
        return "(default)"
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(profiles):
            return profiles[idx]
    except ValueError:
        pass
    print("  Invalid choice.")
    return None


def _prompt_env_values(defaults: dict) -> dict:
    """Interactively prompt the user for env key/value pairs.

    Shows existing values as defaults. User presses Enter to keep the
    default, types a new value to change it, or types 'DONE' to finish.
    """
    print("\n  Enter values (press Enter to keep default, type DONE to finish):\n")

    new_env = {}

    for key, default_val in defaults.items():
        val = input(f"  [{key}] ({default_val}): ").strip()
        new_env[key] = val if val else default_val

    # Allow adding new keys not in defaults
    while True:
        key = input("  New key? (name or DONE): ").strip()
        if not key or key.upper() == "DONE":
            break
        val = input(f"  [{key}]: ").strip()
        new_env[key] = val

    return new_env


def _show_diff(current: dict, target: dict, name: str) -> None:
    """Print a summary of what would change when applying a profile."""
    added = {k: v for k, v in target.items() if k not in current}
    removed = {k: v for k, v in current.items() if k not in target}
    changed = {
        k: (current[k], target[k])
        for k in target
        if k in current and current[k] != target[k]
    }

    any_change = False
    if added:
        any_change = True
        print(f"\n  ➕ Added keys:")
        for k, v in added.items():
            print(f"     {k} = {v}")
    if removed:
        any_change = True
        print(f"\n  ➖ Removed keys:")
        for k, v in removed.items():
            print(f"     {k} = {v}")
    if changed:
        any_change = True
        print(f"\n  🔄 Changed:")
        for k, (old, new) in changed.items():
            print(f"     {k}: {old} → {new}")

    if not any_change:
        print(f"\n  (no changes — env already matches '{name}')")


# ── Commands ──────────────────────────────────────────────────────


def cmd_list():
    """List all saved profiles."""
    profiles = list_profiles()
    if not profiles:
        print("\n  No profiles saved yet. Use 'create' to make one.\n")
    else:
        print(f"\n  Profiles ({len(profiles)}):")
        for i, name in enumerate(profiles, 1):
            env = read_profile(name)
            model = env.get("ANTHROPIC_MODEL", "?")
            effort = env.get("CLAUDE_CODE_EFFORT_LEVEL", "?")
            print(f"    {i}. {name}  [{len(env)} vars]  model={model}  effort={effort}")
    print()
    input("  Press Enter to continue...")


def cmd_change():
    """Apply a profile to settings.json['env']."""
    name = _pick_profile("Apply which profile?")
    if name is None:
        return

    if name == "(default)":
        current = read_env()
        if not current:
            print("\n  Already using default (no env vars set).\n")
            return
        print(f"\n  This will remove all {len(current)} env var(s):")
        for k, v in current.items():
            print(f"    - {k} = {v}")
        confirm = input("\n  Apply default profile? [y/N]: ").strip().lower()
        if confirm == "y":
            apply_default()
            print("  ✅ Default profile applied (all env vars removed).\n")
        else:
            print("  Cancelled.\n")
        return

    current = read_env()
    target = read_profile(name)
    _show_diff(current, target, name)

    confirm = input(f"\n  Apply profile '{name}'? [y/N]: ").strip().lower()
    if confirm == "y":
        apply_profile(name)
        print(f"  ✅ Profile '{name}' applied.\n")
    else:
        print("  Cancelled.\n")


def cmd_create():
    """Create a new profile interactively."""
    name = input("\n  Profile name (e.g., my-openrouter): ").strip()
    if not name:
        print("  Cancelled.")
        return

    if read_profile(name):
        ok = input(f"  Profile '{name}' exists. Overwrite? [y/N]: ").strip().lower()
        if ok != "y":
            print("  Cancelled.")
            return

    defaults = read_env()
    print(f"\n  Creating '{name}'... (defaults = current env)")
    new_env = _prompt_env_values(defaults)

    if not new_env:
        print("  Cancelled.")
        return

    write_profile(name, new_env)
    print(f"\n  ✅ Profile '{name}' saved ({len(new_env)} vars).\n")


def cmd_edit():
    """Edit an existing profile interactively."""
    name = _pick_profile("Edit which profile?")
    if name is None:
        return
    if name == "(default)":
        print("\n  Cannot edit the default profile — it has no env vars.\n")
        return

    current_env = read_profile(name)
    print(f"\n  Editing '{name}'...")
    new_env = _prompt_env_values(current_env)

    if not new_env:
        print("  Cancelled.")
        return

    write_profile(name, new_env)
    print(f"\n  ✅ Profile '{name}' updated ({len(new_env)} vars).\n")


def cmd_delete():
    """Delete a profile."""
    name = _pick_profile("Delete which profile?")
    if name is None:
        return
    if name == "(default)":
        print("\n  Cannot delete the default profile.\n")
        return

    confirm = input(f"\n  Delete profile '{name}'? Cannot undo. [y/N]: ").strip().lower()
    if confirm == "y":
        delete_profile(name)
        print(f"  ✅ Profile '{name}' deleted.\n")
    else:
        print("  Cancelled.\n")


# ── Main entry point ──────────────────────────────────────────────


def _interactive_menu():
    """Display the interactive menu loop."""
    while True:
        current_name = detect_current_profile_name()
        profile_count = len(list_profiles())

        print()
        print("=" * 50)
        print("    Claude Code Env Profile Manager")
        print("=" * 50)
        print(f"    Current profile : {current_name}")
        print(f"    Saved profiles  : {profile_count}")
        print("-" * 50)
        print("    1. 📋  List profiles")
        print("    2. 🔄  Change (apply) profile")
        print("    3. ✨  Create new profile")
        print("    4. ✏️   Edit a profile")
        print("    5. 🗑️   Delete a profile")
        print("    6. 🚪  Exit")
        print("-" * 50)

        choice = input("    Choice [1-6]: ").strip()

        if choice == "1":
            cmd_list()
        elif choice == "2":
            cmd_change()
        elif choice == "3":
            cmd_create()
        elif choice == "4":
            cmd_edit()
        elif choice == "5":
            cmd_delete()
        elif choice == "6":
            print("    Bye!\n")
            sys.exit(0)
        else:
            print("    Invalid choice — enter 1-6.")


def _dispatch_subcommand():
    """Handle direct subcommand usage (non-interactive)."""
    args = sys.argv[1:]
    sub = args[0].lower()

    if sub == "list":
        profiles = list_profiles()
        if not profiles:
            print("No profiles saved.")
        else:
            for name in profiles:
                env = read_profile(name)
                model = env.get("ANTHROPIC_MODEL", "?")
                effort = env.get("CLAUDE_CODE_EFFORT_LEVEL", "?")
                print(f"  {name}  [{len(env)} vars]  model={model}  effort={effort}")

    elif sub == "change":
        if len(args) >= 2:
            name = args[1]
        else:
            name = _pick_profile("Apply which profile?")
        if name == "(default)":
            current = read_env()
            if not current:
                print("Already using default (no env vars set).")
            else:
                print(f"Removing {len(current)} env var(s):")
                for k, v in current.items():
                    print(f"  - {k} = {v}")
                confirm = input("Apply default profile? [y/N]: ").strip().lower()
                if confirm == "y":
                    apply_default()
                    print("✅ Default profile applied (all env vars removed).")
                else:
                    print("Cancelled.")
        elif name and apply_profile(name):
            print(f"✅ Profile '{name}' applied.")
        elif name:
            print(f"❌ Profile '{name}' not found.")

    elif sub == "create":
        if len(args) < 2:
            print("Usage: claude-model-change create <name>")
        else:
            name = args[1]
            defaults = read_env()
            new_env = _prompt_env_values(defaults)
            if new_env:
                write_profile(name, new_env)
                print(f"✅ Profile '{name}' saved ({len(new_env)} vars).")

    elif sub == "edit":
        if len(args) < 2:
            print("Usage: claude-model-change edit <name>")
        else:
            name = args[1]
            if name == "(default)":
                print("Cannot edit the default profile — it has no env vars.")
                return
            current = read_profile(name)
            if current is None:
                print(f"❌ Profile '{name}' not found.")
            else:
                new_env = _prompt_env_values(current)
                if new_env:
                    write_profile(name, new_env)
                    print(f"✅ Profile '{name}' updated.")

    elif sub == "delete":
        if len(args) < 2:
            print("Usage: claude-model-change delete <name>")
        else:
            name = args[1]
            if name == "(default)":
                print("Cannot delete the default profile.")
                return
            confirm = input(f"Delete profile '{name}'? [y/N]: ").strip().lower()
            if confirm == "y":
                if delete_profile(name):
                    print(f"✅ Profile '{name}' deleted.")
                else:
                    print(f"❌ Profile '{name}' not found.")
            else:
                print("Cancelled.")

    else:
        print(f"Unknown command: {sub}")
        print("Available: list, change, create, edit, delete")


def main():
    """Entry point for claude-model-change."""
    if len(sys.argv) > 1:
        _dispatch_subcommand()
    else:
        _interactive_menu()


if __name__ == "__main__":
    main()

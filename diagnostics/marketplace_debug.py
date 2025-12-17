#!/usr/bin/env python3
"""Minimal marketplace manifest consistency check with instrumentation logs."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path("/Users/clementwalter/Documents/rookie-marketplace")
CLAUDE_PLUGINS_DIR = Path("/Users/clementwalter/.claude/plugins")
LOG_PATH = Path("/Users/clementwalter/Documents/rookie-marketplace/.cursor/debug.log")
SESSION_ID = "debug-session"
RUN_ID = "pre-fix"


def _emit(
    hypothesis_id: str, location: str, message: str, data: Dict[str, Any]
) -> None:
    """Append a single NDJSON log line for instrumentation."""
    entry = {
        "sessionId": SESSION_ID,
        "runId": RUN_ID,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=True) + "\n")


def _load_json(path: Path, hypothesis_id: str, location: str) -> Dict[str, Any] | None:
    """Load JSON with error reporting."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - debug helper
        # region agent log
        _emit(
            hypothesis_id,
            location,
            "failed to load json",
            {"path": str(path), "error": str(exc)},
        )
        # endregion
        return None


def _check_commands(plugin_dir: Path, commands: Dict[str, Any]) -> List[str]:
    missing: List[str] = []
    for command_name in commands.keys():
        command_file = plugin_dir / "commands" / f"{command_name}.md"
        if not command_file.exists():
            missing.append(command_name)
    return missing


def _command_headline(path: Path) -> Optional[str]:
    """Return the first non-empty line for a command file, if any."""
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                return line.strip()
    except Exception:
        return None
    return None


def _check_installed_plugins() -> None:
    """Inspect installed_plugins_v2.json paths for existence."""
    installed_path = CLAUDE_PLUGINS_DIR / "installed_plugins_v2.json"
    exists = installed_path.exists()
    # region agent log
    _emit(
        "H7",
        "diagnostics/marketplace_debug.py:83",
        "installed_plugins_v2 presence",
        {"path": str(installed_path), "exists": exists},
    )
    # endregion
    if not exists:
        return

    data = _load_json(installed_path, "H7", "diagnostics/marketplace_debug.py:94")
    if not data:
        return

    plugins = data.get("plugins", {})
    results: Dict[str, Any] = {}
    for key, entries in plugins.items():
        entry_list = entries if isinstance(entries, list) else [entries]
        results[key] = []
        for entry in entry_list:
            install_path = Path(entry.get("installPath", ""))
            results[key].append(
                {
                    "installPath": str(install_path),
                    "pathExists": install_path.exists(),
                    "version": entry.get("version"),
                    "scope": entry.get("scope"),
                }
            )
    # region agent log
    _emit(
        "H7",
        "diagnostics/marketplace_debug.py:113",
        "installed plugin path check",
        {"plugins": results},
    )
    # endregion


def _check_known_marketplaces(expected_name: str) -> None:
    """Verify known_marketplaces.json entry presence."""
    km_path = CLAUDE_PLUGINS_DIR / "known_marketplaces.json"
    exists = km_path.exists()
    # region agent log
    _emit(
        "H8",
        "diagnostics/marketplace_debug.py:129",
        "known_marketplaces presence",
        {"path": str(km_path), "exists": exists},
    )
    # endregion
    if not exists:
        return

    data = _load_json(km_path, "H8", "diagnostics/marketplace_debug.py:139")
    if not data:
        return
    entry = data.get(expected_name)
    # region agent log
    _emit(
        "H8",
        "diagnostics/marketplace_debug.py:145",
        "known_marketplaces entry",
        {"marketplace": expected_name, "present": entry is not None, "entry": entry},
    )
    # endregion


def _check_cache_layout(marketplace_name: str) -> None:
    """Check cache directories for marketplace/plugins."""
    base = CLAUDE_PLUGINS_DIR / "cache" / marketplace_name
    base_exists = base.exists()
    plugins_state: Dict[str, Any] = {}
    if base_exists:
        for plugin_dir in base.iterdir():
            if not plugin_dir.is_dir():
                continue
            plugin_name = plugin_dir.name
            # pick first child dir
            child_dirs = [p for p in plugin_dir.iterdir() if p.is_dir()]
            child = child_dirs[0] if child_dirs else None
            manifest_exists = False
            child_str = str(child) if child else None
            if child:
                manifest_exists = (child / ".claude-plugin" / "plugin.json").exists()
            plugins_state[plugin_name] = {
                "childDir": child_str,
                "manifestExists": manifest_exists,
            }
    # region agent log
    _emit(
        "H9",
        "diagnostics/marketplace_debug.py:171",
        "cache layout check",
        {"base": str(base), "baseExists": base_exists, "plugins": plugins_state},
    )
    # endregion


def main() -> None:
    marketplace_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"
    # region agent log
    _emit(
        "H1",
        "diagnostics/marketplace_debug.py:52",
        "marketplace manifest presence",
        {"path": str(marketplace_path), "exists": marketplace_path.exists()},
    )
    # endregion
    marketplace = _load_json(
        marketplace_path, "H1", "diagnostics/marketplace_debug.py:59"
    )
    if not marketplace:
        return

    plugins = marketplace.get("plugins", [])
    # region agent log
    _emit(
        "H1",
        "diagnostics/marketplace_debug.py:66",
        "marketplace manifest parsed",
        {
            "keys": sorted(marketplace.keys()),
            "pluginCount": len(plugins),
            "pluginNames": [p.get("name") for p in plugins],
        },
    )
    # endregion

    # region agent log
    _emit(
        "H4",
        "diagnostics/marketplace_debug.py:76",
        "marketplace metadata check",
        {
            "hasMetadata": "metadata" in marketplace,
            "metadataKeys": sorted(marketplace.get("metadata", {}).keys()),
            "hasOwner": "owner" in marketplace,
            "ownerKeys": (
                sorted(marketplace.get("owner", {}).keys())
                if isinstance(marketplace.get("owner"), dict)
                else []
            ),
        },
    )
    # endregion

    for plugin in plugins:
        source = plugin.get("source", "")
        plugin_dir = (REPO_ROOT / source).resolve()
        manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
        # region agent log
        _emit(
            "H2",
            "diagnostics/marketplace_debug.py:81",
            "plugin manifest presence",
            {
                "pluginName": plugin.get("name"),
                "source": source,
                "resolvedDirExists": plugin_dir.exists(),
                "manifestExists": manifest_path.exists(),
            },
        )
        # endregion
        manifest = _load_json(
            manifest_path, "H2", "diagnostics/marketplace_debug.py:90"
        )
        if not manifest:
            continue

        # region agent log
        _emit(
            "H5",
            "diagnostics/marketplace_debug.py:106",
            "plugin manifest key coverage",
            {
                "pluginName": plugin.get("name"),
                "missingKeys": sorted(
                    [
                        key
                        for key in (
                            "name",
                            "description",
                            "version",
                            "author",
                            "commands",
                        )
                        if key not in manifest
                    ]
                ),
                "authorKeys": (
                    sorted(manifest.get("author", {}).keys())
                    if isinstance(manifest.get("author"), dict)
                    else []
                ),
            },
        )
        # endregion

        commands = manifest.get("commands", {})
        missing_commands = _check_commands(plugin_dir, commands)
        # region agent log
        _emit(
            "H3",
            "diagnostics/marketplace_debug.py:99",
            "plugin manifest parsed",
            {
                "pluginName": plugin.get("name"),
                "keys": sorted(manifest.keys()),
                "commandCount": len(commands),
                "missingCommands": missing_commands,
            },
        )
        # endregion

        # region agent log
        _emit(
            "H6",
            "diagnostics/marketplace_debug.py:129",
            "command file headlines",
            {
                "pluginName": plugin.get("name"),
                "commands": {
                    name: _command_headline(plugin_dir / "commands" / f"{name}.md")
                    for name in commands.keys()
                },
            },
        )
        # endregion

    _check_installed_plugins()
    marketplace_name = marketplace.get("name") if isinstance(marketplace, dict) else ""
    if marketplace_name:
        _check_known_marketplaces(marketplace_name)
        _check_cache_layout(marketplace_name)


if __name__ == "__main__":
    main()

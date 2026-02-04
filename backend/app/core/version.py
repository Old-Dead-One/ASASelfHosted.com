"""
Version comparison for agent/plugin enforcement.

Sprint 8: MIN_AGENT_VERSION check. Simple semver-style parsing (major.minor.patch).
"""

import re


def _parse_version(version_str: str) -> tuple[int, int, int]:
    """
    Parse a version string into (major, minor, patch).

    Accepts "X", "X.Y", "X.Y.Z". Non-numeric suffixes are stripped.
    Missing parts default to 0. Invalid or empty returns (0, 0, 0).
    """
    if not version_str or not version_str.strip():
        return (0, 0, 0)
    # Strip optional suffix (e.g. "-dev", "+abc")
    base = re.split(r"[-+]", version_str.strip())[0]
    parts = base.split(".")[:3]
    out: list[int] = []
    for i, p in enumerate(parts):
        p = p.strip()
        if not p:
            out.append(0)
            continue
        digits = re.sub(r"[^0-9].*", "", p)
        try:
            out.append(int(digits) if digits else 0)
        except ValueError:
            out.append(0)
    while len(out) < 3:
        out.append(0)
    return (out[0], out[1], out[2])


def is_version_at_least(agent_version: str, min_version: str) -> bool:
    """
    Return True if agent_version >= min_version (semver-style comparison).

    If parsing fails for agent_version, returns False (treat as too old).
    """
    try:
        a = _parse_version(agent_version)
        m = _parse_version(min_version)
        return a >= m
    except Exception:
        return False

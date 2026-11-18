"""Filesystem confinement helpers for all user-controlled work paths."""
from __future__ import annotations

import os
from pathlib import Path

DEFAULT_WORKDIR = "agrodigital_work"


class WorkdirError(ValueError):
    """Raised when a path escapes the configured AgroDigital work directory."""


def workdir_root() -> Path:
    configured = os.environ.get("AGRODIGITAL_WORKDIR", DEFAULT_WORKDIR)
    root = Path(configured).expanduser()
    if not root.is_absolute():
        root = Path.cwd() / root
    # Resolve the root itself once; paths supplied by callers are checked below.
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve(strict=True)


def resolve_work_path(value: str | Path, *, create_parent: bool = False) -> Path:
    """Resolve a relative path inside AGRODIGITAL_WORKDIR; reject traversal and symlinks.

    Absolute paths and any '..' component are rejected even when they happen to
    resolve inside the work directory. Existing symlink components are rejected
    before resolving, preventing a caller from redirecting writes through links.
    """
    raw = os.fspath(value)
    candidate = Path(raw)
    if candidate.is_absolute():
        raise WorkdirError("Absolute paths are not allowed; use a path relative to AGRODIGITAL_WORKDIR.")
    if any(part == ".." for part in candidate.parts):
        raise WorkdirError("Parent-directory traversal ('..') is not allowed.")
    if not raw or raw in {".", "./"}:
        raise WorkdirError("A file or directory path inside AGRODIGITAL_WORKDIR is required.")

    root = workdir_root()
    current = root
    for part in candidate.parts:
        if part in {"", "."}:
            continue
        current = current / part
        if current.is_symlink():
            raise WorkdirError(f"Symlink paths are not allowed: {current}")
    resolved = current.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise WorkdirError("Path escapes AGRODIGITAL_WORKDIR.") from exc

    # Re-check after resolving to catch symlinked parents created between checks.
    probe = resolved
    while probe != root and probe != probe.parent:
        if probe.is_symlink():
            raise WorkdirError(f"Symlink paths are not allowed: {probe}")
        probe = probe.parent
    if create_parent:
        resolved.parent.mkdir(parents=True, exist_ok=True)
        # Ensure parent creation did not introduce a symlink escape.
        parent = resolved.parent.resolve(strict=True)
        try:
            parent.relative_to(root)
        except ValueError as exc:
            raise WorkdirError("Created parent escapes AGRODIGITAL_WORKDIR.") from exc
    return resolved

"""Bounded, checksum-verified HTTPS asset downloads."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


class DownloadError(RuntimeError):
    """Raised when a remote asset cannot be downloaded safely."""


class _HTTPSOnlyRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise DownloadError("Refusing redirect to a non-HTTPS or credential-bearing URL.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download_asset(url: str, destination: str | Path, *, max_bytes: int = 2_000_000_000,
                  sha256: str | None = None, timeout: int = 60, overwrite: bool = False,
                  chunk_size: int = 1024 * 1024) -> dict:
    """Download one HTTPS asset with a hard byte limit and optional SHA-256 check.

    Writes to a sibling .part file and atomically renames only after validation.
    Does not implement resume, STAC signing or authentication.
    """
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Asset URL must be HTTPS and must not embed credentials.")
    if max_bytes <= 0 or timeout <= 0 or chunk_size <= 0:
        raise ValueError("max_bytes, timeout and chunk_size must be positive.")
    if sha256 is not None and (len(sha256) != 64 or any(c not in "0123456789abcdefABCDEF" for c in sha256)):
        raise ValueError("sha256 must contain exactly 64 hexadecimal characters.")

    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not overwrite:
        raise FileExistsError(f"Destination already exists: {target}")
    partial = target.with_name(target.name + ".part")
    digest = hashlib.sha256()
    total = 0
    opener = build_opener(_HTTPSOnlyRedirectHandler())
    request = Request(url, headers={"User-Agent": "AgroDigital-AI/0.3", "Accept": "*/*"})
    try:
        with opener.open(request, timeout=timeout) as response:
            final_url = response.geturl()
            final = urlparse(final_url)
            if final.scheme != "https" or not final.hostname:
                raise DownloadError("Final asset URL is not HTTPS.")
            length = response.headers.get("Content-Length")
            if length:
                try:
                    declared = int(length)
                except ValueError as exc:
                    raise DownloadError("Invalid Content-Length header.") from exc
                if declared < 0 or declared > max_bytes:
                    raise DownloadError(f"Asset exceeds configured size limit ({max_bytes} bytes).")
            with partial.open("wb") as stream:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_bytes:
                        raise DownloadError(f"Asset exceeded configured size limit ({max_bytes} bytes).")
                    digest.update(chunk)
                    stream.write(chunk)
        actual_sha = digest.hexdigest()
        if sha256 and actual_sha.lower() != sha256.lower():
            raise DownloadError("SHA-256 checksum does not match the expected value.")
        if target.exists() and not overwrite:
            raise FileExistsError(f"Destination appeared during download: {target}")
        os.replace(partial, target)
        return {"path": str(target), "bytes": total, "sha256": actual_sha,
                "url": final_url, "verified_checksum": bool(sha256)}
    except (HTTPError, URLError, TimeoutError, OSError, DownloadError) as exc:
        try:
            partial.unlink(missing_ok=True)
        except OSError:
            pass
        if isinstance(exc, (DownloadError, FileExistsError)):
            raise
        raise DownloadError(f"Asset download failed: {exc}") from exc
    finally:
        # A partial file is never presented as a completed asset.
        if partial.exists():
            try:
                partial.unlink()
            except OSError:
                pass

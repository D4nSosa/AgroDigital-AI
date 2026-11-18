"""Bounded, checksum-verified HTTPS asset downloads with SSRF protection."""
from __future__ import annotations

import hashlib
import ipaddress
import os
import socket
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from . import __version__
from .paths import resolve_work_path


class DownloadError(RuntimeError):
    """Raised when a remote asset cannot be downloaded safely."""


def _validate_public_https_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise DownloadError("Asset URL must be HTTPS and must not embed credentials.")
    host = parsed.hostname
    try:
        literal = ipaddress.ip_address(host)
        addresses = [literal]
    except ValueError:
        try:
            addresses = [ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(
                host, parsed.port or 443, type=socket.SOCK_STREAM
            )]
        except (OSError, ValueError) as exc:
            raise DownloadError(f"Could not safely resolve asset host '{host}': {exc}") from exc
    if not addresses:
        raise DownloadError(f"Asset host '{host}' resolved to no addresses.")
    for address in addresses:
        if not address.is_global:
            raise DownloadError(f"Refusing non-public destination address: {address}")
    return host.lower()


class _SafeRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _validate_public_https_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download_asset(url: str, destination: str | Path, *, max_bytes: int = 500_000_000,
                  sha256: str | None = None, timeout: int = 60, overwrite: bool = False,
                  chunk_size: int = 1024 * 1024) -> dict:
    """Download one public HTTPS asset, confined to the configured work directory.

    Resolves and rejects private, loopback, link-local and reserved addresses for
    the initial URL and every redirect. Writes atomically after size/checksum checks.
    """
    _validate_public_https_url(url)
    if max_bytes <= 0 or timeout <= 0 or chunk_size <= 0:
        raise ValueError("max_bytes, timeout and chunk_size must be positive.")
    if sha256 is not None and (len(sha256) != 64 or any(c not in "0123456789abcdefABCDEF" for c in sha256)):
        raise ValueError("sha256 must contain exactly 64 hexadecimal characters.")

    target = resolve_work_path(destination, create_parent=True)
    if target.exists() and not overwrite:
        raise FileExistsError(f"Destination already exists: {target}")
    partial = target.with_name(target.name + ".part")
    digest = hashlib.sha256()
    total = 0
    opener = build_opener(_SafeRedirectHandler())
    request = Request(url, headers={"User-Agent": f"AgroDigital-AI/{__version__}", "Accept": "*/*"})
    try:
        with opener.open(request, timeout=timeout) as response:
            final_url = response.geturl()
            _validate_public_https_url(final_url)
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
        if partial.exists():
            try:
                partial.unlink()
            except OSError:
                pass

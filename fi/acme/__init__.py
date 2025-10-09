# =============================================================================
# FATORI-V • Fault Injection Framework
# File: fi/acme/__init__.py
# -----------------------------------------------------------------------------
# ACME (Essential-Bits → SEM addresses) — Public entry points.
#
# Public API (importable from 'fi.acme'):
#   • load_board(name) -> BoardMap
#       Returns a small object that carries device-level constants (e.g., WF).
#   • extract_device_addresses(ebd_path, board) -> Iterator[str]
#       Streams 10-hex LFAs parsed from a Vivado .ebd essential-bits file.
#   • get_or_build_cached_device_list(ebd_path=..., board_name=..., cache_dir=...) -> Path
#       Produces (or reuses) a cached .txt with one LFA per line for the whole
#       device; meant for area profiles that need a file-backed address list.
#   • scan_ebd_payload_stats(ebd_path) -> (payload_rows, full_32bit_words, ones_bits)
#       Lightweight diagnostic scan to count payload rows, complete 32-bit
#       words and the number of '1' bits; useful for debugging empty outputs.
#
# Debugging (temporary, controlled by env)
#   • If FI_ACME_DEBUG is truthy (“1”, “true”, “on”), this module prints
#     a compact summary about the EBD being parsed (size, payload stats) and
#     shows a few sample LFAs. Unset to silence.
#
# Cache Safety
#   • If FI_ACME_REBUILD is truthy, any existing cache file is ignored and a
#     fresh list is generated.
#   • If a cache file exists but contains zero lines, it is automatically
#     discarded and rebuilt. This avoids stale-empty caches after parser changes.
# =============================================================================

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator, Tuple

from .acme_core import parse_ebd_to_lfas
from .acme_cache import cached_device_path
from .acme_xcku040 import Xcku040Board
from .acme_basys3 import Basys3Board


# ------------------------------ board loader ---------------------------------
def load_board(name: str):
    """
    Return a board/device map object by name. Names are case-insensitive.

    Supported aliases
    -----------------
    UltraScale KU040 family:
        "xcku040", "ku105", "kcu105", "aes-ku040", "aes_ku040", "aes-ku040-db"
    Artix-7 Basys3:
        "basys3", "xc7a35t", "xa35t", "arty-a35t", "a35t"
    """
    key = (name or "").strip().lower()
    if key in ("xcku040", "ku105", "kcu105", "aes-ku040", "aes_ku040", "aes-ku040-db"):
        return Xcku040Board()
    if key in ("basys3", "xc7a35t", "xa35t", "arty-a35t", "a35t"):
        return Basys3Board()
    raise ValueError(f"Unsupported board/device name: {name!r}")


# ------------------------------ debug helpers --------------------------------
def _env_truthy(var_name: str, default: bool = False) -> bool:
    """True if env var is one of: 1, true, yes, on (case-insensitive)."""
    val = os.environ.get(var_name, "")
    if not val:
        return default
    return str(val).strip().lower() in ("1", "true", "yes", "on")


def scan_ebd_payload_stats(ebd_path: str | Path) -> Tuple[int, int, int]:
    """
    Lightweight pre-scan to help diagnose empty-device situations.

    Returns
    -------
    tuple: (payload_rows, full_32bit_words, ones_bits)
      • payload_rows     : number of lines that contain only 0/1 and whitespace.
      • full_32bit_words : number of complete 32-bit words seen when collapsing
                           those rows and chunking per 32 bits.
      • ones_bits        : total number of '1' bits across all complete words.

    Notes
    -----
    • Streaming scan; trailing partial (<32-bit) chunks are ignored.
    • Mirrors the parser’s treatment of payload rows.
    """
    from re import compile as _re
    p = Path(ebd_path)
    payload_rows = 0
    full_words = 0
    ones = 0
    re_payload = _re(r"^[01\s\t]+$")
    with p.open("r", encoding="utf-8", errors="ignore") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            if re_payload.match(line):
                payload_rows += 1
                bits = "".join(ch for ch in line if ch in "01")
                n_full = len(bits) // 32
                full_words += n_full
                if "1" in bits:
                    for i in range(n_full):
                        chunk = bits[i * 32 : (i + 1) * 32]
                        if "1" in chunk:
                            ones += chunk.count("1")
    return payload_rows, full_words, ones


# ------------------------------ device extract -------------------------------
def extract_device_addresses(ebd_path: str | Path, board) -> Iterator[str]:
    """Stream SEM LFAs (10-hex strings) parsed from an EBD file."""
    return parse_ebd_to_lfas(ebd_path, board)


def get_or_build_cached_device_list(
    *,
    ebd_path: str | Path,
    board_name: str,
    cache_dir: str | Path,
) -> Path:
    """
    Build (or reuse) a cached device-wide address list under cache_dir.
    The cache key includes the board name and the EBD file hash/mtime.

    Debug (FI_ACME_DEBUG)
    ---------------------
    Prints: EBD path and size; payload stats; first few LFAs emitted (N controlled
    by FI_ACME_DEBUG_N; default 5).
    """
    ebd_path = Path(ebd_path)
    cache_path = cached_device_path(ebd_path=ebd_path, board_name=board_name, cache_dir=cache_dir)

    debug = _env_truthy("FI_ACME_DEBUG", False)
    debug_n = int(os.environ.get("FI_ACME_DEBUG_N", "5") or "5")
    force_rebuild = _env_truthy("FI_ACME_REBUILD", False)

    if debug:
        try:
            stat = ebd_path.stat()
            print(f"[DEBUG][ACME] EBD: {ebd_path} — size={stat.st_size} bytes")
        except Exception:
            print(f"[DEBUG][ACME] EBD: {ebd_path} — <stat failed>")
        pr, fw, ones = scan_ebd_payload_stats(ebd_path)
        print(f"[DEBUG][ACME] payload_rows={pr}, full_32bit_words={fw}, ones_bits={ones}")

    # Fast path: reuse cache unless forced to rebuild or file is empty
    if cache_path.exists() and not force_rebuild:
        try:
            with cache_path.open("r", encoding="utf-8", errors="ignore") as fh:
                # Peek two lines: 0 -> empty file; 1+ -> usable
                first = fh.readline()
                second = fh.readline()
                has_data = bool(first or second)
        except Exception:
            has_data = False

        if has_data:
            if debug:
                try:
                    n_lines = sum(1 for _ in cache_path.open("r", encoding="utf-8", errors="ignore"))
                except Exception:
                    n_lines = -1
                print(f"[DEBUG][ACME] cache hit: {cache_path} (lines={n_lines})")
            return cache_path
        else:
            # Stale/empty cache — remove and rebuild
            try:
                cache_path.unlink()
                if debug:
                    print(f"[DEBUG][ACME] removed empty cache: {cache_path}")
            except Exception:
                pass

    board = load_board(board_name)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    emitted = 0
    samples: list[str] = []

    with cache_path.open("w", encoding="utf-8") as fh:
        for lfa in extract_device_addresses(ebd_path, board):
            fh.write(lfa + "\n")
            emitted += 1
            if debug and len(samples) < max(0, debug_n):
                samples.append(lfa)

    if debug:
        print(f"[DEBUG][ACME] emitted={emitted} LFAs → {cache_path}")
        if samples:
            print("[DEBUG][ACME] first LFAs:", ", ".join(samples))

    # Defensive: if emitted==0, remove the empty cache so callers can detect it
    if emitted == 0:
        try:
            cache_path.unlink()
        except Exception:
            pass

    return cache_path


# ------------------------------ re-exports -----------------------------------
__all__ = [
    "load_board",
    "extract_device_addresses",
    "get_or_build_cached_device_list",
    "scan_ebd_payload_stats",
]

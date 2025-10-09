# =============================================================================
# ### FATORI-V • Fault Injection Framework
# ### File: fi/area/address_list.py
# -----------------------------------------------------------------------------
# Area profile: address list.
#
# Responsibility
#   • Provide the *next* LFA (10-hex digits) upon request — purely "where".
#   • Perform no sleeps or UART I/O after construction; selection is O(1) per call.
#
# Public API
#   • name: str
#   • describe() -> str            : human-readable summary of the active configuration.
#   • next_address() -> str|None   : next LFA (uppercase 10-hex) or None when exhausted.
#   • iter_addresses() -> Iterable : enumerates remaining LFAs from the current cursor.
#   • __iter__()                   : alias to iter_addresses().
#   • reset()                      : rewinds the internal cursor to the beginning.
#   • end_condition_prompt(reason) : returns a short, human-readable end message for a given reason.
#
# Configuration (case-insensitive keys accepted)
#   • path | file      : path to the address file (one 10-hex LFA per line; '#' comments allowed).
#   • mode | order     : 'sequential' or 'random'. Also accepts legacy alias order='shuffle' for 'random'.
#   • seed             : integer seed used only for 'random' mode. When omitted, the controller supplies
#                        the global run seed via 'seed' to keep selection reproducible.
# -----------------------------------------------------------------------------
from __future__ import annotations

from typing import Iterable, List, Optional, Dict, Any
import os
import re

from fi.area.base import load_addresses_file, apply_ordering


# --- end-condition message dictionary (hardcoded) -----------------------------
_END_MESSAGES = {
    "exhausted": "Address list exhausted.",
}

_HEX10_RE = re.compile(r'^[0-9A-Fa-f]{10}$')


def _norm_keys(d: Dict[str, Any]) -> Dict[str, Any]:
    """Lowercase and strip keys to make argument handling robust."""
    return {str(k).strip().lower(): v for k, v in d.items()}


def _coerce_int(v: Any, default: Optional[int] = None) -> Optional[int]:
    """Parse integers from int|str (supports '0x..' and decimal); returns default on failure."""
    if v is None:
        return default
    try:
        return int(v)
    except Exception:
        try:
            return int(str(v).strip(), 0)
        except Exception:
            return default


class Profile:
    """
    Address list area profile.
    """

    name = "ADDRESS_LIST"

    def __init__(self, **kwargs) -> None:
        # Normalize keys (accept both legacy and new argument names).
        kw = _norm_keys(kwargs)

        # Resolve file path (prefer 'path', accept 'file' as synonym).
        path = kw.pop("path", kw.pop("file", None))
        if not path or not isinstance(path, str):
            raise ValueError("address_list: 'path' (or 'file') is required")
        if not os.path.isfile(path):
            raise ValueError(f"address_list: file not found: {path}")

        # Load raw lines using the shared loader; ignore blanks and '#'-comments.
        raw_addrs: List[str] = load_addresses_file(path)

        # Validate format and normalize to uppercase 10-hex strings.
        addrs: List[str] = []
        for idx, line in enumerate(raw_addrs, start=1):
            s = line.strip()
            if not _HEX10_RE.match(s):
                raise ValueError(f"address_list: invalid LFA at line {idx}: '{line}' (expected 10 hexadecimal digits)")
            addrs.append(s.upper())

        # Determine selection mode: accept 'mode' or legacy 'order'.
        # Allowed values: 'sequential' or 'random'. Legacy alias: order='shuffle' -> 'random'.
        mode_val = kw.pop("mode", None)
        order_val = kw.pop("order", None)

        canonical_mode = None
        for candidate in (mode_val, order_val):
            if candidate is None:
                continue
            s = str(candidate).strip().lower()
            if s in ("sequential", "random"):
                canonical_mode = s
                break
            if s == "shuffle":
                canonical_mode = "random"
                break

        if canonical_mode is None:
            raise ValueError("address_list: 'mode' must be 'sequential' or 'random' (alias accepted: order='shuffle')")

        # Seed handling: used only for random mode. The controller injects the global seed
        # into 'seed' when not explicitly provided to ensure reproducibility.
        seed = _coerce_int(kw.pop("seed", kw.pop("global_seed", None)), None)

        # Apply ordering using the shared helper (maps 'random' -> base's 'shuffle').
        base_order = "shuffle" if canonical_mode == "random" else "sequential"
        ordered = apply_ordering(addrs, order=base_order, seed=seed)

        # Internal storage and cursor.
        self._addrs: List[str] = ordered
        self._idx: int = 0
        self._path: str = path
        self._mode: str = canonical_mode
        self._seed: Optional[int] = seed

    # ---------- public API -----------------------------------------------------
    def describe(self) -> str:
        """Concise human-readable description for banners/log headers."""
        n = len(self._addrs)
        seed_str = f", seed={self._seed}" if (self._seed is not None and self._mode == "random") else ""
        return f"address_list: mode={self._mode}, file={os.path.basename(self._path)}, N={n}{seed_str}"

    def next_address(self) -> Optional[str]:
        """
        Return the next LFA (10-hex, uppercase) or None when the list is exhausted.
        Advances the internal cursor by one on each successful call.
        """
        if self._idx >= len(self._addrs):
            return None
        out = self._addrs[self._idx]
        self._idx += 1
        return out

    def iter_addresses(self) -> Iterable[str]:
        """
        Yield remaining LFAs quickly (no sleeps). This preserves current cursor
        semantics (starts at current position and advances with each yield).
        """
        while self._idx < len(self._addrs):
            yield self.next_address()

    def __iter__(self) -> Iterable[str]:
        """Alias to iter_addresses() for convenience."""
        return self.iter_addresses()

    def reset(self) -> None:
        """Rewind to the first address (useful when a run is re-armed)."""
        self._idx = 0

    def end_condition_prompt(self, reason: str) -> str:
        """
        Return a short human-readable message for a given end reason.

        Recognized reasons for this area profile:
          • 'exhausted'  : address list consumed.

        Any unrecognized reason yields an empty string.
        """
        return _END_MESSAGES.get(str(reason).strip().lower(), "")

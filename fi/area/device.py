# =============================================================================
# FATORI-V • Fault Injection Framework
# File: fi/area/device.py
# -----------------------------------------------------------------------------
# Area profile: device-wide essential-bit injection list.
#
# Responsibilities
#   • Derives a device-wide list of SEM LFAs from a Vivado .ebd essential-bits
#     file using the ACME adapter (fi.acme). The resulting list is cached as a
#     plain .txt (one 10-hex LFA per line) for fast reuse across runs.
#   • Serves addresses sequentially or in a reproducible random order.
#   • Writes a human-friendly copy of the ACME list into the current run’s
#     results folder so operators can easily find the addresses used.
#
# Configuration (CSV key=val via --area-args)
#   • board       : device/board name (e.g., xcku040, basys3). Required.
#   • ebd_file    : path to the Vivado .ebd file. Required.
#   • mode        : 'sequential' | 'random' (in-order vs. shuffled). Optional.
#   • seed        : integer seed for random shuffling. Optional; defaults to global.
#   • cache_dir   : optional override for cache folder (defaults to fi/build/acme).
#   • run_name    : optional, current run name (for results/<run>/<session>/ copy).
#   • session_label : optional, current session label (for results/<run>/<session>/ copy).
#
# Interface
#   • name                : profile name string.
#   • describe() -> str   : short human-readable summary for headers/logs.
#   • next_address()      : iterator yielding one 10-hex LFA per call; None at end.
#   • end_condition_prompt(reason:str) -> str :
#       returns a human-readable message for the end condition 'area_exhausted'.
#       Used by the controller to print/log profile-specific end reasons.
# =============================================================================

from __future__ import annotations

import random
import shutil
from pathlib import Path
from typing import List, Optional

from fi import settings
from fi.acme import get_or_build_cached_device_list, scan_ebd_payload_stats


class Profile:
    """Device-wide essential-bit area source backed by an ACME-generated list."""

    name = "DEVICE"

    def __init__(self, **kwargs) -> None:
        # ---- Parse/normalize kwargs -----------------------------------------
        k = {str(kk).strip().lower(): vv for kk, vv in kwargs.items()}
        self.board: str = str(k.get("board", "")).strip()
        self.ebd_file: str = str(k.get("ebd_file", k.get("file", ""))).strip()
        mode = str(k.get("mode", "sequential")).strip().lower()
        if mode not in ("sequential", "random"):
            raise RuntimeError("device: 'mode' must be 'sequential' or 'random'")
        self.mode = mode

        # Optional run/session for pretty copy into results/<run>/<session>/
        self.run_name: Optional[str] = str(k.get("run_name")).strip() if k.get("run_name") is not None else None
        self.session_label: Optional[str] = str(k.get("session_label")).strip() if k.get("session_label") is not None else None

        # Seed: specific seed overrides; else falls back to global controller seed.
        seed_val = k.get("seed")
        self.seed: Optional[int] = int(seed_val) if seed_val is not None and str(seed_val).strip() != "" else None

        # Cache dir: caller may override; default to fi/build/acme.
        cache_dir = k.get("cache_dir")
        if cache_dir:
            self.cache_dir = Path(str(cache_dir))
        else:
            # Default under repo: fi/build/acme (keep implementation artifacts with code)
            self.cache_dir = Path("fi") / "build" / "acme"

        # ---- Validate required args ------------------------------------------
        if not self.board:
            raise RuntimeError("device: 'board' is required")
        if not self.ebd_file:
            raise RuntimeError("device: 'ebd_file' is required")

        # ---- Build/load the cached device list -------------------------------
        cache_txt = get_or_build_cached_device_list(
            ebd_path=self.ebd_file,
            board_name=self.board,
            cache_dir=self.cache_dir,
        )

        # ---- Read LFAs from cache file (one per line) ------------------------
        addrs: List[str] = []
        with cache_txt.open("r", encoding="utf-8", errors="ignore") as fh:
            for raw in fh:
                s = raw.strip().upper()
                if len(s) == 10 and all(ch in "0123456789ABCDEF" for ch in s):
                    addrs.append(s)

        # ---- Pretty copy into results/<run>/<session>/ for operator visibility
        #      This creates a *copy* named 'acme_injection_addresses.txt' so that
        #      humans look into results/, while the keyed cache remains in fi/build/acme/.
        if self.run_name and self.session_label:
            out_dir = Path(getattr(settings, "LOG_DIR", "results")) / self.run_name / self.session_label
            out_dir.mkdir(parents=True, exist_ok=True)
            friendly_txt = out_dir / "acme_injection_addresses.txt"
            try:
                shutil.copyfile(cache_txt, friendly_txt)
            except Exception:
                # Silent: if copy fails, injection still proceeds using the cache file
                pass

        # ---- Shuffle if requested -------------------------------------------
        if self.mode == "random" and addrs:
            rnd = random.Random(self.seed)
            rnd.shuffle(addrs)

        self._addrs = addrs
        self._idx = 0

        # ---- Diagnose empty lists with actionable detail ---------------------
        if not self._addrs:
            try:
                pr, fw, ones = scan_ebd_payload_stats(self.ebd_file)
                msg = (
                    "device: no addresses found (empty_device) — "
                    f"EBD payload_rows={pr}, full_32bit_words={fw}, ones_bits={ones}. "
                    "If ones_bits=0, regenerate the essential-bits file from the implemented design "
                    "(ensure SEU/Essential Bits is enabled) or confirm the EBD format."
                )
            except Exception:
                msg = "device: no addresses found (empty_device)"
            raise RuntimeError(msg)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    def describe(self) -> str:
        """Short, one-line description for headers/logs."""
        base = f"board={self.board}, ebd={self.ebd_file}, count={len(self._addrs)}"
        if self.mode == "random":
            base += f", mode=random, seed={self.seed}"
        else:
            base += ", mode=sequential"
        return base

    def next_address(self) -> Optional[str]:
        """Return next LFA or None when the device-wide list is exhausted."""
        if self._idx >= len(self._addrs):
            return None
        a = self._addrs[self._idx]
        self._idx += 1
        return a

    # -------------------------------------------------------------------------
    # End-condition prompt (consumed by the controller)
    # -------------------------------------------------------------------------
    def end_condition_prompt(self, reason: str) -> str:
        """
        Provide a human-readable end message for controller printing/logging.
        'reason' is a symbolic code provided by the controller; for area
        profiles today, the natural termination is 'area_exhausted'.
        """
        if reason == "area_exhausted":
            return "Address list exhausted."
        return "Finished."

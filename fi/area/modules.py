# =============================================================================
# FATORI-V • Fault Injection Framework
# File: fi/area/modules.py
# -----------------------------------------------------------------------------
# Area Profile: MODULES
#
# Purpose
#   Yield configuration addresses for one or more modules/pblocks. Each module
#   is backed by a plain text address file (one 10-hex-digit LFA per line),
#   typically produced by ACME from an Essential Bits (.ebd) file filtered by
#   the pblock rectangles associated with that module.
#
# Scope
#   This profile is self-contained and does not perform any UART/SEM operations.
#   It only decides *where* to inject by exposing an iterator over LFAs.
#
# Inputs (case-insensitive keys; accepted via CLI or YAML)
#   Address sources (at least one effective source is required):
#     • path     : single file path
#     • paths    : comma-separated file paths
#     • label    : single module label (resolved as <root>/<label>.txt)
#     • labels   : comma-separated module labels
#     • root     : directory used with label(s) to build file paths
#
#   Mixing strategy when multiple lists are provided:
#     • strategy=concat       Concatenate lists in the given order (default)
#     • strategy=roundrobin   Interleave A0,B0,A1,B1,... until exhaustion
#
#   High-level mode (convenience; mapped to strategy/order below):
#     • mode=sequential       -> strategy=concat,     order=sequential
#     • mode=random           -> strategy=concat,     order=shuffle (seeded)
#     • mode=round_robin      -> strategy=roundrobin, order=sequential
#
#   Post-merge options:
#     • dedupe=true|false     Drop duplicate addresses (preserve first occurrence)
#     • order=sequential|shuffle  Final ordering after merge (if mode not used)
#     • seed=<int>            Seed for reproducible shuffle; if omitted or null,
#                             the orchestrator is expected to supply the run seed.
#
# Design notes
#   • Uses shared helpers from fi.area.base for file loading and ordering.
#   • Keeps behavior deterministic for the same inputs and seed.
#   • Does not attempt ACME generation here (added in Part 2 patch).
# =============================================================================

from __future__ import annotations

from typing import Iterable, List, Optional
import pathlib

from fi.area.base import (
    load_addresses_file,
    apply_ordering,
    dedupe_preserve_order,
    round_robin_merge,
)


def _parse_bool(val: str | bool | None, default: bool = False) -> bool:
    """Parse common boolean spellings from str|bool; None -> default."""
    if isinstance(val, bool):
        return val
    if val is None:
        return default
    s = str(val).strip().lower()
    return s in ("1", "true", "yes", "on")


def _parse_int(val, default: Optional[int] = None) -> Optional[int]:
    """Best-effort integer parse; returns default on None or invalid."""
    if val is None:
        return default
    try:
        return int(str(val).strip())
    except Exception:
        return default


def _mode_to_merge(mode: Optional[str]) -> tuple[str, str]:
    """Map high-level 'mode' to (strategy, order)."""
    if not mode:
        return ("concat", "sequential")
    m = str(mode).strip().lower()
    if m == "random":
        return ("concat", "shuffle")
    if m in ("round_robin", "roundrobin", "round-robin"):
        return ("roundrobin", "sequential")
    return ("concat", "sequential")


class Profile:
    """MODULES area profile: merges per-module address lists and applies ordering."""
    name = "MODULES"

    def __init__(self,
                 *,
                 # File-based selection
                 path: str | None = None,
                 paths: str | None = None,
                 label: str | None = None,
                 labels: str | None = None,
                 root: str = "",
                 # High-level mode (convenience)
                 mode: str | None = None,
                 # Low-level controls (still accepted; overridden by 'mode' when provided)
                 strategy: str = "concat",
                 order: str = "sequential",
                 dedupe: str | bool | None = None,
                 seed: str | int | None = None):
        """Collect inputs, load lists, merge deterministically, and finalize ordering."""
        # -------- Resolve merge/order from 'mode' first (may override below) ---
        mode_strategy, mode_order = _mode_to_merge(mode)
        eff_strategy = (mode_strategy if mode else (strategy or "concat")).strip().lower()
        eff_order    = (mode_order    if mode else (order or "sequential")).strip().lower()

        # -------- Collect file paths from arguments ----------------------------
        file_list: List[pathlib.Path] = []

        if path:
            file_list.append(pathlib.Path(path))

        if paths:
            file_list.extend([pathlib.Path(p.strip()) for p in str(paths).split(",") if p.strip()])

        label_list: List[str] = []
        if label:
            label_list.append(str(label).strip())
        if labels:
            label_list.extend([t.strip() for t in str(labels).split(",") if t.strip()])

        root_dir = pathlib.Path(root) if root else None

        if label_list and root_dir:
            for lb in label_list:
                file_list.append(root_dir / f"{lb}.txt")

        # Validate that we have at least one path source
        if not file_list:
            raise ValueError("MODULES: provide addresses via 'path/paths' or 'label(s)+root'.")

        # Dedup file_list while preserving order
        seen = set()
        unique_files: List[pathlib.Path] = []
        for p in file_list:
            sp = str(p)
            if sp not in seen:
                unique_files.append(p)
                seen.add(sp)

        # -------- Load lists ---------------------------------------------------
        lists: List[List[str]] = [load_addresses_file(str(p)) for p in unique_files]

        # -------- Merge strategy -----------------------------------------------
        if eff_strategy == "roundrobin":
            merged = round_robin_merge(lists)
        else:
            merged = []
            for lst in lists:
                merged.extend(lst)

        # -------- Optional de-duplication --------------------------------------
        self._dedup = _parse_bool(dedupe, default=False)
        if self._dedup:
            merged = dedupe_preserve_order(merged)

        # -------- Final ordering -----------------------------------------------
        self._seed: Optional[int] = _parse_int(seed, default=None)
        self._order = eff_order if eff_order in ("sequential", "shuffle") else "sequential"
        self._addresses: List[str] = apply_ordering(merged, order=self._order, seed=self._seed)

        # -------- Metadata for describe() --------------------------------------
        self._files = [str(p) for p in unique_files]
        self._strategy = eff_strategy

    # -------------------------------------------------------------------------
    # Introspection (presentation-only)
    # -------------------------------------------------------------------------
    def describe(self) -> str:
        parts = [
            f"files={len(self._files)}",
            f"strategy={self._strategy}",
        ]
        if self._dedup:
            parts.append("dedupe=true")
        if self._order != "sequential":
            parts.append(f"order={self._order}")
        if self._seed is not None:
            parts.append(f"seed={self._seed}")
        return f"{', '.join(parts)} (total={len(self._addresses)})"

    # -------------------------------------------------------------------------
    # Address iterator
    # -------------------------------------------------------------------------
    def iter_addresses(self) -> Iterable[str]:
        for a in self._addresses:
            yield a
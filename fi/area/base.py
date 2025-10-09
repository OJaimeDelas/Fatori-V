# =============================================================================
# FATORI-V • Fault Injection Framework
# File: fi/area/base.py
# -----------------------------------------------------------------------------
# Area Profile Interface (WHERE to inject) + Shared Helpers
#
# Design
#   • At runtime, an "area profile" is a thin provider that yields addresses.
#   • The *source* of those addresses (Vivado essential_bits + ACME) is a
#     build-time concern. Runtime profiles simply read the resulting files.
#   • This module centralizes a canonical file reader and a small "ordering"
#     helper so every profile behaves consistently (deterministic, testable).
#
# Contract for area profiles:
#   • Each profile is a single file under fi/area/<name>.py exposing class:
#         class Profile:
#             name: str
#             def __init__(..., **kwargs): ...
#             def describe(self) -> str
#             def iter_addresses(self) -> Iterable[str]
#
# Parameters typically supported by profiles:
#   • path=/root/device.txt                    (device)
#   • path=/root/modA.txt or label=alu,root=/root (module)
#   • order=sequential | shuffle               (address order for the session)
#   • seed=<int>                               (reproducible shuffle)
#   • module profile may also accept:
#       - labels=alu,dsp (multi-module)
#       - paths=/a.txt,/b.txt (multi-files)
#       - strategy=concat|roundrobin (mixing)
#       - dedupe=true|false (preserve order; drop duplicates)
#
# Notes
#   • "order=shuffle" gives a stable randomization per seed (reproducible).
#   • Time profiles decide WHEN to inject; area profiles decide WHERE and in
#     which order to traverse the address space. This keeps the separation
#     clean and makes adding new profiles trivial.
# =============================================================================

from __future__ import annotations

from typing import Iterable, List, Protocol, Sequence, Optional
import random


class AreaProfile(Protocol):
    """Structural protocol (for type-checking and documentation)."""
    name: str
    def describe(self) -> str: ...
    def iter_addresses(self) -> Iterable[str]: ...


# ---------- parsing: shared file loader --------------------------------------
def load_addresses_file(path: str) -> List[str]:
    """
    Read an address list from 'path' using canonical rules:
      - One token per line (LFA hex preferred; FAR,WORD,BIT allowed).
      - Strip whitespace; ignore empty lines and lines starting with '#'.
    Returns a new list in deterministic file order.
    """
    out: List[str] = []
    with open(path, "r") as f:
        for raw in f:
            s = raw.strip()
            if not s or s.startswith("#"):
                continue
            out.append(s)
    return out


# ---------- ordering: sequential vs shuffle ----------------------------------
def apply_ordering(addresses: Sequence[str], order: str = "sequential", seed: Optional[int] = None) -> List[str]:
    """
    Apply the requested order to a sequence of addresses.

    order:
      - "sequential" : return a copy preserving input order
      - "shuffle"    : Fisher-Yates using Random(seed), reproducible per seed

    seed:
      - If None with order="shuffle", a non-deterministic shuffle is performed.
        Prefer providing a seed for reproducibility across runs.
    """
    order = (order or "sequential").strip().lower()
    out = list(addresses)
    if order == "shuffle":
        rnd = random.Random(seed)
        rnd.shuffle(out)
    # else: sequential -> already preserved
    return out


# ---------- list utilities for module profile --------------------------------
def dedupe_preserve_order(items: Sequence[str]) -> List[str]:
    """Remove duplicates while preserving first occurrence order."""
    seen = set()
    out: List[str] = []
    for it in items:
        if it in seen:
            continue
        seen.add(it)
        out.append(it)
    return out


def round_robin_merge(lists: Sequence[Sequence[str]]) -> List[str]:
    """
    Interleave multiple lists element-by-element (A0,B0,C0,A1,B1,C1,...)
    until all lists are exhausted. Deterministic given input lists.
    """
    iters = [iter(lst) for lst in lists]
    out: List[str] = []
    remaining = len(iters)
    # Track exhaustion of individual iterators
    finished = [False] * len(iters)
    while remaining > 0:
        progressed = False
        for idx, it in enumerate(iters):
            if finished[idx]:
                continue
            try:
                out.append(next(it))
                progressed = True
            except StopIteration:
                finished[idx] = True
                remaining -= 1
        if not progressed:
            break
    return out

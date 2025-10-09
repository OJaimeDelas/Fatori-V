# =============================================================================
# FATORI-V • Fault Injection Framework
# File: fi/core/injector.py
# -----------------------------------------------------------------------------
# High-level helpers that drive the SEM protocol for common tasks:
#   • Directed state changes: enter Idle / Observation.
#   • One-shot status query (parsed counters dict).
#   • Assist loop that waits for correction within a timeout.
#   • Blocking injection helper retained for console/manual use.
#
# Notes
#   • Time profiles use fire-and-forget injection (proto.inject_lfa) so TX
#     is never blocked by per-shot waits. SEM responses are captured by the
#     single background RX thread in the controller.
# =============================================================================

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple
import time
import re

from fi.semio.protocol import SemProtocol

_RE_PROMPT  = re.compile(r'^[IOD]>\s*$')
_RE_SC_LINE = re.compile(r'^SC\s+([0-9A-Fa-f]{2})$')
_RE_ECHO_N  = re.compile(r'^[IOD]>\s+N\s', re.IGNORECASE)


def _transport_from_proto(proto: SemProtocol):
    for name in ("tr", "transport", "_tr", "_transport"):
        tr = getattr(proto, name, None)
        if tr is not None:
            return tr
    raise AttributeError("SemProtocol instance does not expose its transport (tr/transport).")


# -------- state transitions ---------------------------------------------------
def ensure_idle(proto: SemProtocol, log) -> List[str]:
    proto.goto_idle()
    tr = _transport_from_proto(proto)
    return tr.read_until_prompt(timeout_s=2.0)

def go_observe(proto: SemProtocol, log) -> List[str]:
    proto.goto_observe()
    tr = _transport_from_proto(proto)
    return tr.read_until_prompt(timeout_s=2.0)


# -------- status --------------------------------------------------------------
def status(proto: SemProtocol, log) -> Dict[str, str]:
    s = proto.status()
    return s or {}


# -------- assist loop ---------------------------------------------------------
def assist_until_fc(proto: SemProtocol, log, timeout_ms: int) -> bool:
    deadline = time.time() + timeout_ms / 1000.0
    while time.time() < deadline:
        s = status(proto, log)
        sc = s.get("SC")
        fc = s.get("FC")
        if sc == "00" and (fc in (None, "00", "0")):
            return True
        time.sleep(0.1)
    return False


# -------- blocking injection (console/manual) --------------------------------
def _parse_inject_ack(lines: Iterable[str]) -> Tuple[bool, bool, bool]:
    echo = False
    sc10 = False
    sc00 = False
    for ln in lines:
        if _RE_ECHO_N.match(ln):
            echo = True
        m = _RE_SC_LINE.match(ln)
        if not m:
            continue
        try:
            val = int(m.group(1), 16)
        except ValueError:
            continue
        if val == 0x10:
            sc10 = True
        elif val == 0x00:
            sc00 = True
    return echo, sc10, sc00


def inject_once(proto: SemProtocol, log, addr: str, timeout_s: float = 2.0) -> List[str]:
    """
    Send 'N <ADDR>' and block until the SEM monitor acknowledges it.
    Intended for console/manual use; time profiles do not use this path.
    """
    proto.inject_lfa(addr)
    tr = _transport_from_proto(proto)
    first = tr.read_until_prompt(timeout_s=timeout_s)
    echo, sc10, sc00 = _parse_inject_ack(first)
    if echo and sc10 and sc00:
        return list(first)
    second = tr.read_until_prompt(timeout_s=0.5)
    echo2, sc102, sc002 = _parse_inject_ack(second)
    out = list(first); out.extend(second)
    if (echo or echo2) and (sc10 or sc102) and (sc00 or sc002):
        return out
    return out

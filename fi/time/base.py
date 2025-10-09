# =============================================================================
# FATORI-V • Fault Injection Framework
# File: fi/time/base.py
# -----------------------------------------------------------------------------
# Base class for time-based injection profiles.
#
# Responsibilities
#   • Concentrates common TX-and-listen discipline for timing profiles:
#       - startup delay handling before the very first shot;
#       - single place for optional ACK gating (via controller-provided tracker);
#       - common address iteration helpers.
#   • Never reads from RX and never blocks the controller’s RX printer.
#   • Leaves scheduling policy to concrete profiles (e.g., uniform, ramp).
#
# Usage
#   • Subclass ProfileBase and implement run(), calling:
#       - self._maybe_first_shot_delay()
#       - self._inject(addr, use_ack=..., ack_timeout_s=...)
#       - use self._addr_iter() to traverse addresses.
# =============================================================================

from __future__ import annotations

import threading
import time
from typing import Optional, Iterable

from fi.semio.protocol import SemProtocol
from fi.log import EventLogger


def _to_float(x, default: float) -> float:
    try:
        return float(x)
    except Exception:
        return float(default)

def _to_int(x, default: Optional[int]) -> Optional[int]:
    if x is None:
        return default
    try:
        return int(x)
    except Exception:
        return default

def _to_bool(x, default: bool) -> bool:
    if isinstance(x, bool):
        return x
    if isinstance(x, str):
        lx = x.strip().lower()
        if lx in ("1", "true", "yes", "on"):  return True
        if lx in ("0", "false", "no", "off"): return False
    return default


class ProfileBase(threading.Thread):
    """
    Common base for time profiles.

    Args (kwargs accepted by __init__):
      - proto (SemProtocol): SEM protocol for TX.
      - log (EventLogger): session logger (deferred writes).
      - area: object providing addresses (iter_addresses/__iter__/addresses/next_address).
      - pause_evt (Event), stop_evt (Event): campaign control events.
      - tx_echo (callable|None): console echo for [SEND] lines.
      - ack_tracker (object|None): provides start() and wait(timeout) if ACK gating is desired.
      - startup_delay_ms (float|str): one-time delay before first shot (default 80ms).
    """

    def __init__(self,
                 *,
                 proto: SemProtocol,
                 log: EventLogger,
                 area,
                 pause_evt: threading.Event,
                 stop_evt: threading.Event,
                 tx_echo=None,
                 ack_tracker=None,
                 startup_delay_ms=80,
                 **_ignored) -> None:
        super().__init__(daemon=True)
        self.proto = proto
        self.log = log
        self.area = area
        self.pause_evt = pause_evt
        self.stop_evt = stop_evt
        self.tx_echo = tx_echo
        self.ack_tracker = ack_tracker
        self._startup_delay_s = max(0.0, _to_float(startup_delay_ms, 80.0) / 1000.0)
        self._first_shot = True
        # Termination reason filled by subclasses ("area_exhausted", "max_reached", etc.)
        self.finished_reason: Optional[str] = None

    # ----- address iteration helpers ----------------------------------------
    def _addr_iter(self) -> Iterable[str]:
        """
        Provide an iterator over address strings (LFAs). Supports:
          - area.iter_addresses()
          - iter(area)
          - iter(area.addresses)
          - generator wrapping area.next_address()
        """
        if hasattr(self.area, "iter_addresses"):
            return self.area.iter_addresses()
        if hasattr(self.area, "__iter__"):
            return iter(self.area)
        if hasattr(self.area, "addresses"):
            return iter(self.area.addresses)

        class _Iter:
            def __init__(self, provider): self.p = provider
            def __iter__(self): return self
            def __next__(self):
                if hasattr(self.p, "next_address"):
                    nxt = self.p.next_address()
                    if nxt is None:
                        raise StopIteration
                    return nxt
                raise StopIteration
        return _Iter(self.area)

    # ----- first shot delay --------------------------------------------------
    def _maybe_first_shot_delay(self) -> None:
        """
        Apply a one-time, small delay before the first injection. This keeps
        initial campaign TX decoupled from any preceding console output and
        improves capture of the very first acknowledgement without any RX read.
        """
        if self._first_shot and self._startup_delay_s > 0.0:
            time.sleep(self._startup_delay_s)
        self._first_shot = False

    # ----- TX helper (optional ACK gating) -----------------------------------
    def _inject(self, addr: str, *, use_ack: bool = False, ack_timeout_s: float = 1.5) -> None:
        """
        Send 'N <addr>' with TX-first semantics. The RX printer remains the
        sole consumer. Optional ACK gating waits on SC 00 via ack_tracker.
        """
        msg = f"N {addr}"
        self.log.log_tx(msg)
        if callable(self.tx_echo):
            self.tx_echo(msg)
        if use_ack and self.ack_tracker is not None:
            self.ack_tracker.start()
        self.proto.inject_lfa(addr)
        if use_ack and self.ack_tracker is not None:
            self.ack_tracker.wait(ack_timeout_s)

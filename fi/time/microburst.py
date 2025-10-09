# =============================================================================
# ### FATORI-V • Fault Injection Framework
# ### File: fi/time/microburst.py
# -----------------------------------------------------------------------------
# Time profile: Micro-burst injections (k-shot bursts).
#
# Role
#   • Decide *when* to inject bursts of shots:
#       - Each burst emits 'shots_per_burst' shots spaced by 'intra_burst_period_s'.
#       - Bursts are spaced by 'inter_burst_s'.
#   • If intra_burst_period_s <= 0, shots inside the burst are sent as fast as possible.
#   • Does not read from RX; transmission uses the base helper.
#
# Configuration (case-insensitive keys accepted)
#   • shots_per_burst                : integer ≥1 (shots per burst).
#   • inter_burst_s | off_period_s   : (optional) seconds between bursts (default: 1.0).
#   • intra_burst_period_s           : (optional) seconds between shots inside a burst (default: 0.0 = ASAP).
#   • bursts                         : (optional) total number of bursts; if omitted, runs until duration/external stop.
#   • duration_s | duration          : (optional) overall time limit for the profile.
#   • ack (bool) / ack_timeout_s     : (optional) ACK gating between shots.
#   • max_shots                      : (optional) cap on total shots (profile-complete).
#   • startup_delay_ms               : (optional) one-time delay before first TX.
#
# End-condition messages (hardcoded)
#   • 'duration_elapsed' : "Duration limit reached."
#   • 'profile_complete' : "Requested number of bursts completed."
#   • 'max_reached'      : "Maximum shots limit reached."
# -----------------------------------------------------------------------------
from __future__ import annotations

import time
from typing import Optional, Dict, Any

from fi.time.base import ProfileBase


# --- end-condition message dictionary (hardcoded) -----------------------------
_END_MESSAGES = {
    "duration_elapsed": "Duration limit reached.",
    "profile_complete": "Requested number of bursts completed.",
    "max_reached": "Maximum shots limit reached.",
}


def _norm_keys(d: Dict[str, Any]) -> Dict[str, Any]:
    return {str(k).strip().lower(): v for k, v in d.items()}


def _coerce_float(v: Any, default: float) -> float:
    if v is None:
        return float(default)
    try:
        return float(v)
    except Exception:
        try:
            return float(str(v).strip())
        except Exception:
            return float(default)


def _coerce_int(v: Any, default: Optional[int] = None) -> Optional[int]:
    if v is None:
        return default
    try:
        return int(v)
    except Exception:
        try:
            return int(float(v))
        except Exception:
            return default


def _coerce_bool(v: Any, default: bool) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        return default
    s = str(v).strip().lower()
    if s in ("1", "true", "yes", "on"):
        return True
    if s in ("0", "false", "no", "off"):
        return False
    return default


class Profile(ProfileBase):
    """
    Micro-burst scheduler.

    Emits bursts of shots separated by an inter-burst gap. Within a burst, shots
    are spaced by a configurable intra-burst period, or ASAP if zero/negative.
    """

    name = "MICROBURST"

    def __init__(self, **kwargs) -> None:
        kw = _norm_keys(kwargs)

        self.shots_per_burst: int = max(1, _coerce_int(kw.pop("shots_per_burst", 1), 1) or 1)
        self.inter_burst_s: float = max(0.0, _coerce_float(kw.pop("inter_burst_s", kw.pop("off_period_s", 1.0)), 1.0))
        self.intra_burst_period_s: float = _coerce_float(kw.pop("intra_burst_period_s", 0.0), 0.0)

        # Optional total bursts; when provided, profile completes after emitting them.
        self.bursts: Optional[int] = _coerce_int(kw.pop("bursts", None), None)
        # Optional duration bound and shot cap.
        self.duration_s: Optional[float] = None
        if "duration_s" in kw or "duration" in kw:
            dv = _coerce_float(kw.pop("duration_s", kw.pop("duration", 0.0)), 0.0)
            self.duration_s = dv if dv > 0.0 else None
        self.max_shots: Optional[int] = _coerce_int(kw.pop("max_shots", None), None)

        # ACK gating.
        self.ack = _coerce_bool(kw.pop("ack", False), False)
        self.ack_timeout_s = _coerce_float(kw.pop("ack_timeout_s", 1.5), 1.5)

        # Wait tuning/time source.
        self._spin_threshold_s = 0.002
        self._now = time.perf_counter

        # Wire base class (proto/log/area/pause/stop/tx_echo/ack_tracker/startup_delay_ms).
        super().__init__(**kw)

        # Config log (most important first).
        try:
            msg = (
                f"MICROBURST config: shots_per_burst={self.shots_per_burst}, "
                f"intra_burst_period_s={self.intra_burst_period_s:.6f}, inter_burst_s={self.inter_burst_s:.6f}"
            )
            if self.bursts is not None:
                msg += f", bursts={self.bursts}"
            if self.duration_s is not None:
                msg += f", duration_s={self.duration_s:.6f}"
            self.log.log_prof_time(msg)
        except Exception:
            pass

    # ----- helpers -------------------------------------------------------------
    def _sleep_until(self, t_deadline: float) -> None:
        while True:
            rem = t_deadline - self._now()
            if rem <= 0.0:
                return
            if rem > self._spin_threshold_s:
                time.sleep(rem - self._spin_threshold_s)
            else:
                while self._now() < t_deadline:
                    pass
                return

    def end_condition_prompt(self, reason: str) -> str:
        return _END_MESSAGES.get(str(reason).strip().lower(), "")

    def _log_profile_end(self, reason: str) -> None:
        try:
            msg = self.end_condition_prompt(reason)
            self.log.log_info(f"Time profile [{self.name}] finished.{(' ' + msg) if msg else ''}")
        except Exception:
            pass

    # ----- main loop -----------------------------------------------------------
    def run(self) -> None:
        try:
            addr_it = self._addr_iter()
            total_shots = 0
            t0: Optional[float] = None
            bursts_emitted = 0

            # First-shot setup delay (before starting timing windows).
            self._maybe_first_shot_delay()
            t0 = self._now()

            while True:
                if self.stop_evt.is_set():
                    break

                # Duration guard.
                if self.duration_s is not None:
                    if (self._now() - t0) >= self.duration_s:
                        self.finished_reason = "duration_elapsed"
                        self._log_profile_end(self.finished_reason)
                        return

                # Bursts count guard.
                if self.bursts is not None and bursts_emitted >= self.bursts:
                    self.finished_reason = "profile_complete"
                    self._log_profile_end(self.finished_reason)
                    return

                # Burst start.
                shots_in_this_burst = 0
                while shots_in_this_burst < self.shots_per_burst:
                    if self.stop_evt.is_set():
                        break

                    # Pause handling.
                    while self.pause_evt.is_set() and not self.stop_evt.is_set():
                        time.sleep(0.05)
                    if self.stop_evt.is_set():
                        break

                    # Max shots guard (global).
                    if self.max_shots is not None and total_shots >= self.max_shots:
                        self.finished_reason = "max_reached"
                        self._log_profile_end(self.finished_reason)
                        return

                    # Obtain next address; if area exhausts, upper layer handles it.
                    try:
                        addr = next(addr_it)
                    except StopIteration:
                        try:
                            self.log.log_info("Exiting. Creating log file.")
                        except Exception:
                            pass
                        return

                    # Transmit (ACK optional).
                    if self.ack and self.ack_timeout_s > 0.0 and self.ack_tracker is not None:
                        self.ack_tracker.start()
                        self._inject(addr, use_ack=False)
                        self.ack_tracker.wait(self.ack_timeout_s)
                    else:
                        self._inject(addr, use_ack=False)

                    total_shots += 1
                    shots_in_this_burst += 1

                    # Intra-burst spacing.
                    if shots_in_this_burst < self.shots_per_burst and self.intra_burst_period_s > 0.0:
                        deadline = self._now() + self.intra_burst_period_s
                        self._sleep_until(deadline)

                # Completed one burst.
                bursts_emitted += 1

                # Inter-burst spacing.
                if self.inter_burst_s > 0.0:
                    deadline = self._now() + self.inter_burst_s
                    self._sleep_until(deadline)

            # Exit note for deferred logger.
            try:
                self.log.log_info("Exiting. Creating log file.")
            except Exception:
                pass

        except Exception:
            try:
                self.log.log_info("Exiting. Creating log file.")
            except Exception:
                pass
            return

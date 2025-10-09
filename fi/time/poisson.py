# =============================================================================
# ### FATORI-V • Fault Injection Framework
# ### File: fi/time/poisson.py
# -----------------------------------------------------------------------------
# Time profile: Poisson process with exponential inter-arrival times. Supports
# optional overall duration. Only profile-owned end conditions are marked here.
#
# Public API
#   • name: str
#   • run(): profile scheduler loop (thread entrypoint).
#   • end_condition_prompt(reason) -> str : short message explaining the end reason.
#
# Configuration (case-insensitive keys accepted)
#   • rate_hz | rate | hz | lambda_hz | λ  → mean rate in Hz.
#   • period_s | period | period_sec       → mean period in seconds (overrides rate).
#   • duration_s | duration                → optional total run time.
#   • seed                                 → optional RNG seed for reproducibility.
#   • ack (bool) / ack_timeout_s (float)   → optional ACK gating.
#   • max_shots (int)                      → optional shot cap.
#   • startup_delay_ms (float)             → one-time pre-TX delay.
# -----------------------------------------------------------------------------
from __future__ import annotations

import time
import random
from typing import Optional, Dict, Any

from fi.time.base import ProfileBase


# --- end-condition message dictionary (hardcoded) -----------------------------
_END_MESSAGES = {
    "duration_elapsed": "Duration limit reached.",
    "max_reached": "Maximum shots limit reached.",
}

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


def _coerce_int(v: Any, default: Optional[int]) -> Optional[int]:
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


def _norm_keys(d: Dict[str, Any]) -> Dict[str, Any]:
    return {str(k).strip().lower(): v for k, v in d.items()}


class Profile(ProfileBase):
    """
    Poisson time profile runner.

    Draws an exponential waiting time before each shot with parameter λ. When
    a duration is provided, the profile stops at duration end. This class does
    not read from RX. It logs a profile-specific message on completion when a
    profile-owned end condition occurs.
    """

    name = "POISSON"

    def __init__(self, **kwargs) -> None:
        kw = _norm_keys(kwargs)

        # Mean period takes priority over rate resolution.
        period_val = kw.pop("period_s", kw.pop("period", kw.pop("period_sec", None)))
        rate_val = kw.pop("rate_hz", kw.pop("rate", kw.pop("hz", kw.pop("lambda_hz", kw.pop("λ", None)))))
        period_s = _coerce_float(period_val, -1.0) if period_val is not None else -1.0
        if period_s is not None and period_s > 0.0:
            self.lambda_hz = 1.0 / float(period_s)
        else:
            self.lambda_hz = float(_coerce_float(rate_val, 1.0))

        # Optional duration bound.
        self.duration_s: Optional[float] = None
        if "duration_s" in kw or "duration" in kw:
            self.duration_s = float(_coerce_float(kw.pop("duration_s", kw.pop("duration", 0.0)), 0.0))
            if self.duration_s <= 0.0:
                self.duration_s = None

        # RNG, ACK gating, and shot cap.
        seed_val = _coerce_int(kw.pop("seed", None), None)
        self._rng = random.Random(seed_val) if seed_val is not None else random.Random()

        self.ack = _coerce_bool(kw.pop("ack", False), False)
        self.ack_timeout_s = _coerce_float(kw.pop("ack_timeout_s", 1.5), 1.5)
        self.max_shots: Optional[int] = _coerce_int(kw.pop("max_shots", None), None)

        # Wait tuning and time source.
        self._spin_threshold_s = 0.002
        self._now = time.perf_counter

        # Wire base class (proto/log/area/pause/stop/tx_echo/ack_tracker/startup_delay_ms).
        super().__init__(**kw)

        # Log effective configuration (most important first).
        try:
            mean_period = (1.0 / self.lambda_hz) if self.lambda_hz > 0.0 else 0.0
            if self.duration_s is not None:
                self.log.log_prof_time(
                    f"POISSON config: rate_hz={self.lambda_hz:.6f}, mean_period_s={mean_period:.6f}, duration_s={self.duration_s:.6f}"
                )
            else:
                self.log.log_prof_time(
                    f"POISSON config: rate_hz={self.lambda_hz:.6f}, mean_period_s={mean_period:.6f}"
                )
        except Exception:
            pass

    # --- helpers ---------------------------------------------------------------
    def _sleep_until(self, t_deadline: float) -> None:
        while True:
            now = self._now()
            remaining = t_deadline - now
            if remaining <= 0.0:
                return
            if remaining > self._spin_threshold_s:
                time.sleep(remaining - self._spin_threshold_s)
            else:
                while self._now() < t_deadline:
                    pass
                return

    def end_condition_prompt(self, reason: str) -> str:
        """
        Return a short human-readable message for a given end reason.

        Recognized reasons for this time profile:
          • 'duration_elapsed' : elapsed time reached 'duration_s'.
          • 'max_reached'      : shot count reached 'max_shots'.

        Any unrecognized reason yields an empty string.
        """
        return _END_MESSAGES.get(str(reason).strip().lower(), "")

    def _log_profile_end(self, reason: str) -> None:
        """Emit a single INFO line describing the end condition for this profile."""
        try:
            msg = self.end_condition_prompt(reason)
            self.log.log_info(f"Time profile [{self.name}] finished.{(' ' + msg) if msg else ''}")
        except Exception:
            pass

    # --- main loop -------------------------------------------------------------
    def run(self) -> None:
        try:
            addr_it = self._addr_iter()
            shots = 0
            t0: Optional[float] = None

            for addr in addr_it:
                if self.stop_evt.is_set():
                    break

                # Pause handling.
                while self.pause_evt.is_set() and not self.stop_evt.is_set():
                    time.sleep(0.05)
                if self.stop_evt.is_set():
                    break

                # Duration end check.
                if self.duration_s is not None and t0 is not None:
                    if (self._now() - t0) >= self.duration_s:
                        self.finished_reason = "duration_elapsed"
                        self._log_profile_end(self.finished_reason)
                        return

                # Max shots guard.
                if self.max_shots is not None and shots >= self.max_shots:
                    self.finished_reason = "max_reached"
                    self._log_profile_end(self.finished_reason)
                    return

                self._maybe_first_shot_delay()

                if t0 is None:
                    t0 = self._now()

                # Draw inter-arrival interval.
                interval_s = (self._rng.expovariate(self.lambda_hz) if self.lambda_hz > 0.0 else 0.0)

                # Transmit with optional ACK gating.
                if self.ack and self.ack_timeout_s > 0.0 and self.ack_tracker is not None:
                    self.ack_tracker.start()
                    self._inject(addr, use_ack=False)
                    self.ack_tracker.wait(self.ack_timeout_s)
                    next_deadline = self._now() + interval_s if interval_s > 0.0 else self._now()
                else:
                    self._inject(addr, use_ack=False)
                    next_deadline = self._now() + interval_s if interval_s > 0.0 else self._now()

                shots += 1

                if interval_s > 0.0:
                    self._sleep_until(next_deadline)

            # Time profile does not log area exhaustion here by design.

            # Exit note near the end of the run.
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

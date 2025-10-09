# =============================================================================
# ### FATORI-V • Fault Injection Framework
# ### File: fi/time/ramp.py
# -----------------------------------------------------------------------------
# Time profile: linear ramp of injection rate. Supports time-based interpolation
# (duration) and step-based interpolation (steps). Optional hold at the end rate.
# Only profile-owned end conditions are marked here.
#
# Public API
#   • name: str
#   • run(): profile scheduler loop (thread entrypoint).
#   • end_condition_prompt(reason) -> str : short message explaining the end reason.
#
# Configuration (case-insensitive keys accepted)
#   • start_hz | start_rate | start_frequency_hz  OR  start_period_s | start_period.
#   • end_hz   | end_rate   | end_frequency_hz    OR  end_period_s   | end_period.
#     (for each edge, period has precedence over rate when both are provided)
#   • duration_s | duration : time-based ramp; stops at duration end.
#   • steps                 : step-based ramp; interpolates over N shots.
#   • hold_end_rate         : only for steps mode without duration; when true,
#                             keep injecting at the end rate indefinitely.
#   • ack / ack_timeout_s   : optional ACK gating.
#   • max_shots             : optional shot cap (applies across ramp and hold).
#   • startup_delay_ms      : one-time pre-TX delay.
# -----------------------------------------------------------------------------
from __future__ import annotations

import time
from typing import Optional, Dict, Any

from fi.time.base import ProfileBase


# --- end-condition message dictionary (hardcoded) -----------------------------
_END_MESSAGES = {
    "duration_elapsed": "Duration limit reached.",
    "max_reached": "Maximum shots limit reached.",
    "profile_complete": "Ramp completed.",
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


def _resolve_edge(period_val: Any, rate_val: Any, default_rate: float) -> float:
    period_s = _coerce_float(period_val, -1.0) if period_val is not None else -1.0
    if period_s is not None and period_s > 0.0:
        return 1.0 / period_s
    return _coerce_float(rate_val, default_rate)


class Profile(ProfileBase):
    """
    Linear ramp scheduler.

    Computes per-shot deadlines by interpolating the frequency from start to
    end using elapsed time (duration-based) or shot index (step-based). When
    step-based and configured to hold, cadence remains at the end rate until
    external stop. When duration-based, the profile stops at duration end.
    For area exhaustion, no profile completion is set here.
    """

    name = "RAMP"

    def __init__(self, **kwargs) -> None:
        kw = _norm_keys(kwargs)

        start_period = kw.pop("start_period_s", kw.pop("start_period", None))
        start_rate   = kw.pop("start_hz", kw.pop("start_rate", kw.pop("start_frequency_hz", None)))
        end_period   = kw.pop("end_period_s", kw.pop("end_period", None))
        end_rate     = kw.pop("end_hz", kw.pop("end_rate", kw.pop("end_frequency_hz", None)))

        self.start_hz = float(_resolve_edge(start_period, start_rate, 1.0))
        self.end_hz   = float(_resolve_edge(end_period,   end_rate,   self.start_hz))

        # Duration-based or step-based interpolation selection.
        self.duration_s: Optional[float] = None
        if "duration_s" in kw or "duration" in kw:
            self.duration_s = float(_coerce_float(kw.pop("duration_s", kw.pop("duration", 0.0)), 0.0))
            if self.duration_s <= 0.0:
                self.duration_s = None

        self.steps: Optional[int] = None
        if self.duration_s is None:
            self.steps = _coerce_int(kw.pop("steps", None), None)
            if self.steps is not None and self.steps <= 1:
                self.steps = 1

        # Hold behavior for step-based ramps without duration.
        self.hold_end_rate: bool = _coerce_bool(kw.pop("hold_end_rate", True), True)

        # Optional ACK gating & shot cap.
        self.ack = _coerce_bool(kw.pop("ack", False), False)
        self.ack_timeout_s = _coerce_float(kw.pop("ack_timeout_s", 1.5), 1.5)
        self.max_shots: Optional[int] = _coerce_int(kw.pop("max_shots", None), None)

        # Wait tuning and time source.
        self._spin_threshold_s = 0.002
        self._now = time.perf_counter

        # Wire base class.
        super().__init__(**kw)

        # Log effective configuration in importance order.
        try:
            if self.duration_s is not None:
                self.log.log_prof_time(
                    f"RAMP config: start_hz={self.start_hz:.6f}, end_hz={self.end_hz:.6f}, duration_s={self.duration_s:.6f}"
                )
            elif self.steps is not None:
                self.log.log_prof_time(
                    f"RAMP config: start_hz={self.start_hz:.6f}, end_hz={self.end_hz:.6f}, steps={self.steps}, hold_end_rate={self.hold_end_rate}"
                )
            else:
                self.log.log_prof_time(
                    f"RAMP config: start_hz={self.start_hz:.6f}, end_hz={self.end_hz:.6f}, mode=hold_end"
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
          • 'profile_complete' : step-based ramp completed with hold_end_rate=false.

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
            step_mode = (self.duration_s is None)

            for addr in addr_it:
                if self.stop_evt.is_set():
                    break

                # Pause handling.
                while self.pause_evt.is_set() and not self.stop_evt.is_set():
                    time.sleep(0.05)
                if self.stop_evt.is_set():
                    break

                # Duration end check (time-based ramps stop at duration).
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

                # Instantaneous cadence.
                if self.duration_s is not None:
                    # Time-based interpolation.
                    elapsed = max(0.0, self._now() - t0)
                    if self.duration_s > 0.0:
                        alpha = max(0.0, min(1.0, elapsed / self.duration_s))
                    else:
                        alpha = 1.0
                    rate_hz = (self.start_hz + (self.end_hz - self.start_hz) * alpha)
                elif self.steps is not None:
                    # Step-based interpolation based on shot index.
                    alpha = max(0.0, min(1.0, float(shots) / float(max(1, self.steps - 1))))
                    rate_hz = (self.start_hz + (self.end_hz - self.start_hz) * alpha)
                else:
                    # No interpolation params provided: hold at end rate.
                    rate_hz = self.end_hz

                period_s = (1.0 / rate_hz) if rate_hz > 0.0 else 0.0

                # Transmit with optional ACK gating.
                if self.ack and self.ack_timeout_s > 0.0 and self.ack_tracker is not None:
                    self.ack_tracker.start()
                    self._inject(addr, use_ack=False)
                    self.ack_tracker.wait(self.ack_timeout_s)
                    next_deadline = self._now() + period_s if period_s > 0.0 else self._now()
                else:
                    self._inject(addr, use_ack=False)
                    next_deadline = self._now() + period_s if period_s > 0.0 else self._now()

                shots += 1

                # If step-based without duration and not holding, stop at ramp end.
                if step_mode and self.steps is not None and not self.hold_end_rate:
                    if shots >= self.steps:
                        self.finished_reason = "profile_complete"
                        self._log_profile_end(self.finished_reason)
                        return

                # Wait for next deadline (best-effort if period<=0).
                if period_s > 0.0:
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

# =============================================================================
# ### FATORI-V • Fault Injection Framework
# ### File: fi/time/uniform.py
# -----------------------------------------------------------------------------
# Time profile: uniform injection rate at a fixed cadence, with optional
# overall duration. Only profile-owned end conditions are marked here.
#
# Public API
#   • name: str
#   • run(): profile scheduler loop (thread entrypoint).
#   • end_condition_prompt(reason) -> str : short message explaining the end reason.
#
# Configuration (case-insensitive keys accepted)
#   • rate_hz | rate | hz | freq_hz | frequency_hz  → injections per second.
#   • period_s | period | period_sec                → seconds between shots.
#       (period_* has priority over rate_* when both are present)
#   • duration_s | duration                         → optional total run time.
#   • ack (bool) / ack_timeout_s (float)            → optional ACK gating.
#   • max_shots (int)                               → optional shot cap.
#   • startup_delay_ms (float)                      → small one-time pre-TX delay.
# -----------------------------------------------------------------------------
from __future__ import annotations

import time
from typing import Optional, Dict, Any

from fi.time.base import ProfileBase


# --- end-condition message dictionary (hardcoded) -----------------------------
_END_MESSAGES = {
    "duration_elapsed": "Duration limit reached.",
    "max_reached": "Maximum shots limit reached.",
}

def _coerce_float(v: Any, default: float) -> float:
    """
    Best-effort float parse from str|int|float; fall back to default.
    Accepts strings like '0x10' by parsing as int with base auto-detection
    when a direct float() cast fails.
    """
    if v is None:
        return float(default)
    try:
        return float(v)
    except Exception:
        try:
            return float(int(str(v), 0))
        except Exception:
            return float(default)


def _coerce_int(v: Any, default: Optional[int]) -> Optional[int]:
    """Best-effort int parse from str|int|float; fall back to default."""
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
    """Parse common boolean representations from str|int|bool."""
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
    """Lowercase and strip keys to make argument handling robust."""
    return {str(k).strip().lower(): v for k, v in d.items()}


class Profile(ProfileBase):
    """
    Uniform time profile runner.

    Provides constant-rate cadence using a drift-corrected scheduler. This
    class does not read from RX. Transmission is delegated to the base helper
    (_inject). When a profile-owned end condition is met, an INFO log line is
    emitted with a profile-specific end message.
    """

    name = "UNIFORM"

    def __init__(self, **kwargs) -> None:
        kw = _norm_keys(kwargs)

        # Resolve period first (takes precedence over rate).
        period_candidates = ("period_s", "period", "period_sec")
        period_val = None
        for k in period_candidates:
            if k in kw:
                period_val = kw.pop(k)
                break

        # Resolve rate if period not provided.
        rate_candidates = ("rate_hz", "rate", "hz", "freq_hz", "frequency_hz")
        rate_val = None
        for k in rate_candidates:
            if k in kw:
                rate_val = kw.pop(k)
                break

        period_s = _coerce_float(period_val, -1.0)
        rate_hz = _coerce_float(rate_val, 1.0)

        if period_s is not None and period_s >= 0.0:
            self.period = float(period_s)
        else:
            self.period = (1.0 / rate_hz) if rate_hz > 0.0 else 0.0

        # Optional duration bound.
        self.duration_s: Optional[float] = None
        duration_val = kw.pop("duration_s", kw.pop("duration", None)) if "duration_s" in kw or "duration" in kw else None
        if duration_val is not None:
            dv = _coerce_float(duration_val, 0.0)
            self.duration_s = dv if dv > 0.0 else None

        # Optional ACK gating & limits.
        self.ack = _coerce_bool(kw.pop("ack", False), False)
        self.ack_timeout_s = _coerce_float(kw.pop("ack_timeout_s", 1.5), 1.5)
        self.max_shots: Optional[int] = _coerce_int(kw.pop("max_shots", None), None)

        # Wait tuning and time source.
        self._spin_threshold_s = 0.002
        self._now = time.perf_counter

        # Parent wiring (proto/log/area/pause/stop/tx_echo/ack_tracker/startup_delay_ms).
        super().__init__(**kw)

        # Log effective configuration: most important first (rate → period → duration).
        try:
            eff_rate = (1.0 / self.period) if self.period > 0 else 0.0
            if self.duration_s is not None:
                self.log.log_prof_time(
                    f"UNIFORM config: rate_hz={eff_rate:.6f}, period_s={self.period:.6f}, duration_s={self.duration_s:.6f}"
                )
            else:
                self.log.log_prof_time(
                    f"UNIFORM config: rate_hz={eff_rate:.6f}, period_s={self.period:.6f}"
                )
        except Exception:
            pass

    # --- helpers ---------------------------------------------------------------
    def _sleep_until(self, t_deadline: float) -> None:
        """Hybrid wait: coarse sleep then a short spin to meet the deadline precisely."""
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
        """
        Emit a single INFO line describing the end condition for this profile.
        The formatting is kept consistent with other profiles.
        """
        try:
            msg = self.end_condition_prompt(reason)
            self.log.log_info(f"Time profile [{self.name}] finished.{(' ' + msg) if msg else ''}")
        except Exception:
            # Logging must never prevent a clean shutdown.
            pass

    # --- main loop -------------------------------------------------------------
    def run(self) -> None:
        try:
            addr_it = self._addr_iter()
            shots = 0

            # Base time for drift-corrected cadence.
            t0 = self._now()
            k = 0  # next shot index in schedule t = t0 + k*period

            for addr in addr_it:
                if self.stop_evt.is_set():
                    break

                # Pause handling (non-busy).
                while self.pause_evt.is_set() and not self.stop_evt.is_set():
                    time.sleep(0.05)
                if self.stop_evt.is_set():
                    break

                # Duration end check (only when configured).
                if self.duration_s is not None:
                    if (self._now() - t0) >= self.duration_s:
                        self.finished_reason = "duration_elapsed"
                        self._log_profile_end(self.finished_reason)
                        return

                # Max shots guard (optional).
                if self.max_shots is not None and shots >= self.max_shots:
                    self.finished_reason = "max_reached"
                    self._log_profile_end(self.finished_reason)
                    return

                # One-time small pre-TX delay.
                self._maybe_first_shot_delay()

                # Transmit now; ACK gating optionally anchors cadence to ACK.
                if self.ack and self.ack_timeout_s > 0.0 and self.ack_tracker is not None:
                    self.ack_tracker.start()
                    self._inject(addr, use_ack=False)
                    self.ack_tracker.wait(self.ack_timeout_s)
                    k += 1
                    next_deadline = (self._now() + self.period) if self.period > 0.0 else self._now()
                else:
                    self._inject(addr, use_ack=False)
                    k += 1
                    next_deadline = (t0 + k * self.period) if self.period > 0.0 else self._now()

                shots += 1

                # Cadence wait.
                if self.period > 0.0:
                    self._sleep_until(next_deadline)

            # Time profile does not log area exhaustion here by design.

            # Exit note near the end of the run; included in the deferred log buffer.
            try:
                self.log.log_info("Exiting. Creating log file.")
            except Exception:
                pass

        except Exception:
            # Ensure the exit note is still captured on unexpected errors.
            try:
                self.log.log_info("Exiting. Creating log file.")
            except Exception:
                pass
            return

# =============================================================================
# ### FATORI-V • Fault Injection Framework
# ### File: fi/time/mmpp2.py
# -----------------------------------------------------------------------------
# Time profile: Two-State Markov–Modulated Poisson Process (MMPP-2).
#
# Role
#   • Decide *when* to inject using a Poisson process whose rate switches
#     between two states: LOW and HIGH.
#   • Switching is governed by a two-state Markov chain evaluated after each
#     shot: with probabilities p_low_to_high and p_high_to_low.
#   • Does not read from RX; transmission uses the base helper.
#
# Configuration (case-insensitive keys accepted)
#   • low_hz | lambda_low_hz        : Poisson rate in the LOW state (Hz).
#   • high_hz | lambda_high_hz      : Poisson rate in the HIGH state (Hz).
#   • p_low_to_high | p_lh          : Probability in [0,1] to switch LOW→HIGH after a shot.
#   • p_high_to_low | p_hl          : Probability in [0,1] to switch HIGH→LOW after a shot.
#   • start_state                   : "low" or "high" (default: "low").
#   • duration_s | duration         : (optional) overall time limit for the profile.
#   • seed                          : (optional) RNG seed for reproducibility.
#   • ack (bool) / ack_timeout_s    : (optional) ACK gating between shots.
#   • max_shots                     : (optional) cap on number of shots (profile-complete).
#   • startup_delay_ms              : (optional) one-time delay before first TX.
#
# End-condition messages (hardcoded)
#   • 'duration_elapsed' : "Duration limit reached."
#   • 'max_reached'      : "Maximum shots limit reached."
#   • 'profile_complete' : "Profile shot limit reached."
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
    "profile_complete": "Profile shot limit reached.",
}


def _norm_keys(d: Dict[str, Any]) -> Dict[str, Any]:
    """Lowercase/strip keys for robust argument handling."""
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
    Two-State MMPP scheduler.

    After each shot, the state may switch with configured probabilities.
    In each state, inter-arrival times are exponential with the state's rate.
    """

    name = "MMPP2"

    def __init__(self, **kwargs) -> None:
        kw = _norm_keys(kwargs)

        # Rates for LOW/HIGH states.
        low_hz = _coerce_float(kw.pop("low_hz", kw.pop("lambda_low_hz", 1.0)), 1.0)
        high_hz = _coerce_float(kw.pop("high_hz", kw.pop("lambda_high_hz", 10.0)), 10.0)
        self.low_hz = float(max(0.0, low_hz))
        self.high_hz = float(max(0.0, high_hz))

        # State-transition probabilities (per shot).
        self.p_lh = max(0.0, min(1.0, _coerce_float(kw.pop("p_low_to_high", kw.pop("p_lh", 0.05)), 0.05)))
        self.p_hl = max(0.0, min(1.0, _coerce_float(kw.pop("p_high_to_low", kw.pop("p_hl", 0.05)), 0.05)))

        # Initial state.
        start_state = str(kw.pop("start_state", "low")).strip().lower()
        self.state_is_high = (start_state == "high")

        # Optional duration bound.
        self.duration_s: Optional[float] = None
        if "duration_s" in kw or "duration" in kw:
            dv = _coerce_float(kw.pop("duration_s", kw.pop("duration", 0.0)), 0.0)
            self.duration_s = dv if dv > 0.0 else None

        # Optional limits and gating.
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

        # Config log (most important first).
        try:
            self.log.log_prof_time(
                f"MMPP2 config: low_hz={self.low_hz:.6f}, high_hz={self.high_hz:.6f}, "
                f"p_lh={self.p_lh:.3f}, p_hl={self.p_hl:.3f}, start_state={'HIGH' if self.state_is_high else 'LOW'}"
                + (f", duration_s={self.duration_s:.6f}" if self.duration_s is not None else "")
            )
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

                # Duration check.
                if self.duration_s is not None and t0 is not None:
                    if (self._now() - t0) >= self.duration_s:
                        self.finished_reason = "duration_elapsed"
                        self._log_profile_end(self.finished_reason)
                        return

                # Max shots guard.
                if self.max_shots is not None and shots >= self.max_shots:
                    self.finished_reason = "profile_complete"
                    self._log_profile_end(self.finished_reason)
                    return

                # First-shot setup.
                self._maybe_first_shot_delay()
                if t0 is None:
                    t0 = self._now()

                # Draw exponential interval according to current state.
                lam = self.high_hz if self.state_is_high else self.low_hz
                interval_s = (self._rng.expovariate(lam) if lam > 0.0 else 0.0)

                # Transmit with optional ACK gating.
                if self.ack and self.ack_timeout_s > 0.0 and self.ack_tracker is not None:
                    self.ack_tracker.start()
                    self._inject(addr, use_ack=False)
                    self.ack_tracker.wait(self.ack_timeout_s)
                    deadline = self._now() + interval_s if interval_s > 0.0 else self._now()
                else:
                    self._inject(addr, use_ack=False)
                    deadline = self._now() + interval_s if interval_s > 0.0 else self._now()

                shots += 1

                # State transition after the shot, per configured probabilities.
                if self.state_is_high:
                    if self._rng.random() < self.p_hl:
                        self.state_is_high = False
                else:
                    if self._rng.random() < self.p_lh:
                        self.state_is_high = True

                if interval_s > 0.0:
                    self._sleep_until(deadline)

            # Time profile does not signal area exhaustion; controller handles it.

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

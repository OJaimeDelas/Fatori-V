# =============================================================================
# ### FATORI-V • Fault Injection Framework
# ### File: fi/time/trace.py
# -----------------------------------------------------------------------------
# Time profile: Trace-driven schedule.
#
# Role
#   • Decide *when* to inject based on times loaded from a file.
#   • File format: one numeric value per non-comment line; '#' starts a comment.
#   • Two modes:
#       - mode='relative'  : values are absolute times (seconds) since t0.
#       - mode='intervals' : values are inter-arrival gaps Δt in seconds.
#   • Optional 'repeat' to replay the whole sequence multiple times.
#   • Does not read from RX; transmission uses the base helper.
#
# Configuration (case-insensitive keys accepted)
#   • path | file                   : path to schedule file.
#   • mode                          : 'relative' (default) or 'intervals'.
#   • repeat                        : (optional) integer ≥1; number of full-sequence repeats.
#   • duration_s | duration         : (optional) overall time limit; stops when elapsed ≥ duration_s.
#   • ack (bool) / ack_timeout_s    : (optional) ACK gating between shots.
#   • max_shots                     : (optional) cap on number of shots (profile-complete).
#   • startup_delay_ms              : (optional) one-time delay before first TX.
#
# End-condition messages (hardcoded)
#   • 'schedule_exhausted' : "Schedule exhausted."
#   • 'duration_elapsed'   : "Duration limit reached."
#   • 'max_reached'        : "Maximum shots limit reached."
#   • 'profile_complete'   : "Profile shot limit reached."
# -----------------------------------------------------------------------------
from __future__ import annotations

import os
import time
from typing import Optional, Dict, Any, List

from fi.time.base import ProfileBase


# --- end-condition message dictionary (hardcoded) -----------------------------
_END_MESSAGES = {
    "schedule_exhausted": "Schedule exhausted.",
    "duration_elapsed": "Duration limit reached.",
    "max_reached": "Maximum shots limit reached.",
    "profile_complete": "Profile shot limit reached.",
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


class Profile(ProfileBase):
    """
    Trace-driven scheduler.

    Loads a list of times from a file and schedules injections accordingly.
    """

    name = "TRACE"

    def __init__(self, **kwargs) -> None:
        kw = _norm_keys(kwargs)

        # Path to schedule file.
        path = kw.pop("path", kw.pop("file", None))
        if not path or not isinstance(path, str):
            raise ValueError("trace: 'path' (or 'file') is required")
        if not os.path.isfile(path):
            raise ValueError(f"trace: file not found: {path}")
        self._path = path

        # Mode selection.
        mode = str(kw.pop("mode", "relative")).strip().lower()
        if mode not in ("relative", "intervals"):
            raise ValueError("trace: 'mode' must be 'relative' or 'intervals'")
        self._mode = mode

        # Optional duration bound.
        self.duration_s: Optional[float] = None
        if "duration_s" in kw or "duration" in kw:
            dv = _coerce_float(kw.pop("duration_s", kw.pop("duration", 0.0)), 0.0)
            self.duration_s = dv if dv > 0.0 else None

        # Optional repeats and max shots.
        self.repeat: int = max(1, _coerce_int(kw.pop("repeat", 1), 1) or 1)
        self.max_shots: Optional[int] = _coerce_int(kw.pop("max_shots", None), None)

        # ACK gating.
        self.ack = bool(kw.pop("ack", False))
        self.ack_timeout_s = _coerce_float(kw.pop("ack_timeout_s", 1.5), 1.5)

        # Wait tuning and time source.
        self._spin_threshold_s = 0.002
        self._now = time.perf_counter

        # Wire base class.
        super().__init__(**kw)

        # Load and parse schedule.
        self._schedule = self._load_schedule(self._path, self._mode)

        # Log configuration (most important first).
        try:
            self.log.log_prof_time(
                f"TRACE config: path={os.path.basename(self._path)}, mode={self._mode}, "
                f"entries={len(self._schedule)}, repeat={self.repeat}"
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

    @staticmethod
    def _load_schedule(path: str, mode: str) -> List[float]:
        """
        Load a schedule file:
          - Lines starting with '#' or empty/whitespace-only lines are ignored.
          - Each remaining line must parse as a float (seconds).
          - For 'relative' mode: values are non-decreasing times since t0.
          - For 'intervals' mode: values are strictly positive Δt.
        Returns list of floats.
        """
        vals: List[float] = []
        with open(path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, start=1):
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                try:
                    x = float(s)
                except Exception:
                    raise ValueError(f"trace: invalid number at line {idx}: '{line.rstrip()}'")
                if mode == "intervals":
                    if x < 0.0:
                        raise ValueError(f"trace: negative interval at line {idx}: {x}")
                else:  # relative
                    if x < 0.0:
                        raise ValueError(f"trace: negative time at line {idx}: {x}")
                vals.append(float(x))

        if not vals:
            raise ValueError("trace: schedule is empty")

        if mode == "relative":
            # Warn-like behavior: ensure non-decreasing; if not, we still sort to be safe.
            # We avoid raising to keep robustness; ordering deviations will be corrected here.
            vals = sorted(vals)

        return vals

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

            # First-shot setup.
            self._maybe_first_shot_delay()

            for r in range(self.repeat):
                # Reset reference time at the beginning of each sequence.
                if t0 is None:
                    t0 = self._now()
                seq_start = t0 if self._mode == "relative" else self._now()

                for val in self._schedule:
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

                    # Obtain next address; if area exhausts, the orchestrator handles it.
                    try:
                        addr = next(addr_it)
                    except StopIteration:
                        # End of area; let upper layers switch modes. Do not set a reason here.
                        # Ensure exit note is recorded.
                        try:
                            self.log.log_info("Exiting. Creating log file.")
                        except Exception:
                            pass
                        return

                    # Determine deadline for this shot.
                    if self._mode == "relative":
                        deadline = seq_start + float(val)
                    else:  # intervals
                        deadline = self._now() + float(val)

                    # Wait to deadline (if in the future).
                    now = self._now()
                    if deadline > now:
                        self._sleep_until(deadline)

                    # Transmit with optional ACK gating.
                    if self.ack and self.ack_timeout_s > 0.0 and self.ack_tracker is not None:
                        self.ack_tracker.start()
                        self._inject(addr, use_ack=False)
                        self.ack_tracker.wait(self.ack_timeout_s)
                    else:
                        self._inject(addr, use_ack=False)

                    shots += 1

                if self.stop_evt.is_set():
                    break

            # Finished all repeats and schedule entries.
            self.finished_reason = "schedule_exhausted"
            self._log_profile_end(self.finished_reason)

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

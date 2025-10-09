# =============================================================================
# FATORI-V • Fault Injection Framework
# File: fi/log/events.py
# -----------------------------------------------------------------------------
# Event logger for fault-injection sessions.
#
# Responsibilities
#   • Collect timestamped events in memory (deferred write).
#   • Enforce per-class enablement (tags toggled via fi/settings.py).
#   • Emit a single per-session file with a structured header:
#       - Title
#       - Run/session/device/baud/SEM clock
#       - Area/Time profile summary (provided by the controller)
#       - "Logged tags:" list (only enabled tags) + configuration note
#       - Conventions block
#   • Flush to disk on close, preserving event order.
#
# Tag classes (selectable via settings):
#   - "SEM CMD"   : UART monitor traffic ([SEND]/[RECV]); TX entries carry a '*'
#   - "INFO"      : informational controller events
#   - "ERROR"     : error conditions detected by the controller
#   - "CNSL CMD"  : user console commands (if the caller chooses to log them)
#   - "CNSL MODE" : console mode transitions (MAN↔DRI)
#   - "PROF TIME" : time-profile lifecycle/changes
#   - "PROF AREA" : area-profile lifecycle/changes
#
# Notes
#   • The logger does not print to console; it only records to file.
#   • Writing is deferred until close() to minimize I/O on the bench path.
# =============================================================================

from __future__ import annotations

import os
import time
from typing import Dict, List, Optional, Tuple

from fi import settings
from fi.console import console_settings as cs


class EventLogger:
    """
    Per-session event accumulator with a structured header. Callers push events
    with specific helpers (log_tx/log_rx/log_info/log_error/log_prof_time/
    log_prof_area). On close(), the header and all accumulated events are written
    to 'injection_log.txt'.
    """

    _FILENAME = "injection_log.txt"

    def __init__(self, *, run_name: str, session_label: str, defer: bool = True) -> None:
        # Session identity and output path
        self._run = run_name
        self._session = session_label
        self._root_dir = getattr(settings, "LOG_DIR", "results")
        self._out_dir = os.path.join(self._root_dir, self._run, self._session)
        self._path = os.path.join(self._out_dir, self._FILENAME)

        # Deferred storage and timing origin
        self._t0 = time.monotonic()
        self._events: List[Tuple[float, str, str]] = []  # (delta_s, tag, text)

        # Header base fields
        self._hdr_device: Optional[str] = None
        self._hdr_baud: Optional[int] = None
        self._hdr_sem_freq: Optional[int] = None

        # Header profile summary
        self._hdr_area_name: Optional[str] = None
        self._hdr_area_kwargs: Optional[Dict[str, str]] = None
        self._hdr_time_name: Optional[str] = None
        self._hdr_time_kwargs: Optional[Dict[str, str]] = None

        # Write mode (kept for completeness; logger currently always defers)
        self._defer = bool(defer)

    # ------------------------------- header population ------------------------
    def set_header(
        self,
        *,
        device: Optional[str] = None,
        baud: Optional[int] = None,
        sem_freq_hz: Optional[int] = None,
        area_profile: Optional[str] = None,
        area_kwargs: Optional[Dict[str, str]] = None,
        time_profile: Optional[str] = None,
        time_kwargs: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Populate or update header fields. The controller may call this multiple
        times as information becomes available; the last value for each field wins.
        """
        if device is not None:
            self._hdr_device = device
        if baud is not None:
            self._hdr_baud = baud
        if sem_freq_hz is not None:
            self._hdr_sem_freq = sem_freq_hz
        if area_profile is not None:
            self._hdr_area_name = area_profile
        if area_kwargs is not None:
            self._hdr_area_kwargs = dict(area_kwargs)
        if time_profile is not None:
            self._hdr_time_name = time_profile
        if time_kwargs is not None:
            self._hdr_time_kwargs = dict(time_kwargs)

    # --------------------------------- log helpers ----------------------------
    def log_tx(self, cmd: str) -> None:
        """
        UART transmit monitor entry.
        TX entries are marked with a trailing '*' by convention. The distance
        between the command text and the '*' is configurable to improve
        readability in dense logs. The spacing is controlled by the console
        setting LOG_TX_ASTERISK_SPACES.
        """
        try:
            pad = int(getattr(cs, "LOG_TX_ASTERISK_SPACES", 15))
        except Exception:
            pad = 15
        if pad < 0:
            pad = 0
        spacing = " " * pad
        self._append("SEM CMD", f"[SEND]: {cmd}{spacing}*")

    def log_rx(self, line: str) -> None:
        """UART receive monitor entry."""
        self._append("SEM CMD", f"[RECV]: {line}")

    def log_info(self, msg: str) -> None:
        """Generic informational event."""
        self._append("INFO", msg)

    def log_error(self, msg: str) -> None:
        """Error event."""
        self._append("ERROR", msg)

    def log_prof_time(self, msg: str) -> None:
        """Time-profile lifecycle/change event."""
        self._append("PROF TIME", msg)

    def log_prof_area(self, msg: str) -> None:
        """Area-profile lifecycle/change event."""
        self._append("PROF AREA", msg)

    # ----------------------------------- close() ------------------------------
    def close(self) -> None:
        """
        Write header + events to disk. The header includes:
          • Title
          • Run/session/device/baud/SEM clock
          • Area/Time profile summary
          • "Logged tags:" list containing only enabled tags + configuration note
          • Conventions (e.g., TX '*' marker)
        """
        os.makedirs(self._out_dir, exist_ok=True)
        width = 110
        rule_big = "=" * width   # major delimiter
        rule_small = "-" * width # minor delimiter
        lines: List[str] = []

        # Title
        lines.append(rule_big)
        lines.append("Fatori-V - SEM log")
        lines.append(rule_small)

        # Header: session context
        lines.append(f"Run: {self._run}")
        lines.append(f"Session: {self._session}")
        if self._hdr_device is not None and self._hdr_baud is not None:
            lines.append(f"Device: {self._hdr_device} @ {self._hdr_baud} baud")
        elif self._hdr_device is not None:
            lines.append(f"Device: {self._hdr_device}")
        if self._hdr_sem_freq is not None:
            lines.append(f"SEM clock: {self._hdr_sem_freq} Hz")

        # Area/Time summary
        lines.append(rule_small)
        if self._hdr_area_name is not None:
            lines.append(f"Area Profile: {self._hdr_area_name}")
            if self._hdr_area_kwargs:
                for k in sorted(self._hdr_area_kwargs.keys()):
                    lines.append(f"  {k:<10}: {self._hdr_area_kwargs[k]}")
        if self._hdr_time_name is not None:
            lines.append(f"Time Profile: {self._hdr_time_name}")
            if self._hdr_time_kwargs:
                for k in sorted(self._hdr_time_kwargs.keys()):
                    lines.append(f"  {k:<10}: {self._hdr_time_kwargs[k]}")

        # Logged tags (enabled only) + configuration note
        lines.append(rule_small)
        lines.append("Logged tags:")
        for tag in self._enabled_tag_names():
            lines.append(f"  - {tag}")
        lines.append("TAG Log can be configured in fi/settings.py")

        # Conventions block (right before event stream)
        lines.append(rule_small)
        lines.append("Conventions:")
        lines.append("  - Transmission ([SEND]) entries are marked with '*' in this log.")
        lines.append(rule_big)

        # Events
        for (dt, tag, text) in self._events:
            lines.append(f"[+{dt:8.3f}s] {tag} {text}")

        # Persist
        with open(self._path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    # ------------------------------ internals ---------------------------------
    def _append(self, tag: str, text: str) -> None:
        """Append if tag is enabled."""
        if not self._tag_enabled(tag):
            return
        dt = time.monotonic() - self._t0
        self._events.append((dt, tag, text))

    def _enabled_tag_names(self) -> List[str]:
        """Return the enabled tag names, filtered to the set known by the logger."""
        mapping = [
            ("SEM CMD",   bool(getattr(settings, "LOG_SEM_CMD_ENABLED", True))),
            ("INFO",      bool(getattr(settings, "LOG_INFO_ENABLED", True))),
            ("ERROR",     bool(getattr(settings, "LOG_ERR_ENABLED", True))),
            ("CNSL CMD",  bool(getattr(settings, "LOG_CNSL_CMD_ENABLED", True))),
            ("CNSL MODE", bool(getattr(settings, "LOG_CNSL_MODE_ENABLED", True))),
            ("PROF TIME", bool(getattr(settings, "LOG_PROF_TIME_ENABLED", True))),
            ("PROF AREA", bool(getattr(settings, "LOG_PROF_AREA_ENABLED", True))),
        ]
        return [name for (name, enabled) in mapping if enabled]

    def _tag_enabled(self, tag: str) -> bool:
        """Per-tag toggle resolution against fi/settings.py."""
        if tag == "SEM CMD":
            return bool(getattr(settings, "LOG_SEM_CMD_ENABLED", True))
        if tag == "INFO":
            return bool(getattr(settings, "LOG_INFO_ENABLED", True))
        if tag == "ERROR":
            return bool(getattr(settings, "LOG_ERR_ENABLED", True))
        if tag == "CNSL CMD":
            return bool(getattr(settings, "LOG_CNSL_CMD_ENABLED", True))
        if tag == "CNSL MODE":
            return bool(getattr(settings, "LOG_CNSL_MODE_ENABLED", True))
        if tag == "PROF TIME":
            return bool(getattr(settings, "LOG_PROF_TIME_ENABLED", True))
        if tag == "PROF AREA":
            return bool(getattr(settings, "LOG_PROF_AREA_ENABLED", True))
        return False


# -----------------------------------------------------------------------------
# End of file
# -----------------------------------------------------------------------------

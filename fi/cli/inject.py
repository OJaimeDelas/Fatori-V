# =============================================================================
# FATORI-V • Fault Injection Framework
# File: fi/cli/inject.py
# -----------------------------------------------------------------------------
# CLI: One-shot injection (no automatic Observation).
#
# Behavior:
#   - Ensures Idle (I>) before injecting, to keep monitor state predictable.
#   - Forwards the address token verbatim to 'N' (SEM injection command).
#   - Captures a status snapshot after injection for basic counters sanity.
#
# Address token formats accepted:
#   - LFA hex (e.g., 0008000090D)
#   - FAR,WORD,BIT (WORD and BIT are decimal), e.g., 0008000090D,12,5
#
# Logging:
#   - TX/RX lines and INFO events are recorded to a per-session log file.
#   - Log header includes device/baud/SEM clock to aid analysis.
# =============================================================================

from __future__ import annotations

import argparse
import sys

from fi import settings
from fi.semio.transport import SerialConfig, SemTransport
from fi.semio.protocol import SemProtocol

# Logging import allows both new and legacy paths for flexibility.
try:
    from fi.log import EventLogger
except Exception:  # pragma: no cover
    from fi.log.events import EventLogger

from fi.core.injector import ensure_idle, inject_once, status


def _log_rx_lines(log: EventLogger, lines):
    """
    Mirror each received text line into the session log as RX entries.
    This preserves UART context alongside higher-level events.
    """
    for l in lines:
        log.log_rx(l)


def main(argv=None):
    # ----------------------------- CLI parsing ------------------------------
    # Only the address token is required; other options default from settings.
    p = argparse.ArgumentParser(description="One-shot injection (no auto-observation).")
    p.add_argument("--addr", required=True, help="Address token: LFA hex or FAR,WORD,BIT")
    p.add_argument("--dev", default=settings.DEFAULT_SEM_DEVICE, help="Serial device path")
    p.add_argument("--baud", type=int, default=settings.BAUDRATE, help="Serial baud rate")
    p.add_argument("--run-name", default=settings.DEFAULT_RUN_NAME, help="Run name for results/<run_name>/...")
    p.add_argument("--session", default=settings.DEFAULT_SESSION_LABEL, help="Session/benchmark label")
    args = p.parse_args(argv)

    # --------------------------- Transport + log ----------------------------
    # The logger writes a header with connection details and defers body writes
    # until close, so each session produces a single coherent file.
    cfg = SerialConfig(device=args.dev, baud=args.baud)
    log = EventLogger(run_name=args.run_name, session_label=args.session, defer=settings.DEFER_LOG_WRITE)
    tr = SemTransport(cfg)

    try:
        tr.open()
        log.set_header(device=cfg.device, baud=cfg.baud, sem_freq_hz=settings.SEM_FREQ_HZ)

        # Protocol facade manages prompt-synchronized exchanges with the monitor.
        proto = SemProtocol(tr)
        proto.sync_prompt()

        # Enter Idle, run injection verbatim, then capture a quick counters snapshot.
        _log_rx_lines(log, ensure_idle(proto, log))
        _log_rx_lines(log, inject_once(proto, log, args.addr))

        s = status(proto, log)
        for k, v in s.items():
            log.log_rx(f"{k} {v}")

    finally:
        # On exit, flush deferred log lines and close the UART cleanly.
        log.close()
        tr.close()


if __name__ == "__main__":
    sys.exit(main())

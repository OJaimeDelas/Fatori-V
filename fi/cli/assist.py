# =============================================================================
# FATORI-V • Fault Injection Framework
# File: fi/cli/assist.py
# -----------------------------------------------------------------------------
# CLI: Assistance window for correction.
#
# Behavior:
#   - Enters Observation (O>) and polls status until FC increments or timeout.
#   - Returns to Idle (I>) before exiting.
#   - Prints a one-line summary to stdout; logs full TX/RX and events.
#
# Typical usage:
#   - Run immediately after an injection to confirm whether SEM corrected it.
# =============================================================================

from __future__ import annotations

import argparse
import sys

from fi import settings
from fi.semio.transport import SerialConfig, SemTransport
from fi.semio.protocol import SemProtocol

try:
    from fi.log import EventLogger
except Exception:  # pragma: no cover
    from fi.log.events import EventLogger

from fi.core.injector import assist_until_fc


def main(argv=None):
    # ----------------------------- CLI parsing ------------------------------
    p = argparse.ArgumentParser(description="Assist window for SEM correction (Observation until FC increments or timeout).")
    p.add_argument("--timeout-ms", type=int, default=1500, help="Max wait for FC to increment (milliseconds)")
    p.add_argument("--dev", default=settings.DEFAULT_SEM_DEVICE, help="Serial device path")
    p.add_argument("--baud", type=int, default=settings.BAUDRATE, help="Serial baud rate")
    p.add_argument("--run-name", default=settings.DEFAULT_RUN_NAME, help="Run name for results/<run_name>/...")
    p.add_argument("--session", default=settings.DEFAULT_SESSION_LABEL, help="Session/benchmark label")
    args = p.parse_args(argv)

    # --------------------------- Transport + log ----------------------------
    cfg = SerialConfig(device=args.dev, baud=args.baud)
    log = EventLogger(run_name=args.run_name, session_label=args.session, defer=settings.DEFER_LOG_WRITE)
    tr = SemTransport(cfg)

    try:
        tr.open()
        log.set_header(device=cfg.device, baud=cfg.baud, sem_freq_hz=settings.SEM_FREQ_HZ)

        proto = SemProtocol(tr)
        proto.sync_prompt()

        # Run assist loop and provide immediate terminal feedback.
        cleared = assist_until_fc(proto, log, args.timeout_ms)
        print("ASSIST: CLEARED" if cleared else "ASSIST: TIMEOUT")

    finally:
        log.close()
        tr.close()


if __name__ == "__main__":
    sys.exit(main())

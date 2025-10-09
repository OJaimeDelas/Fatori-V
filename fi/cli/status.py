# =============================================================================
# FATORI-V • Fault Injection Framework
# File: fi/cli/status.py
# -----------------------------------------------------------------------------
# CLI: Status / heartbeat utility.
#
# Behavior:
#   - One-shot or periodic (--watch) counter snapshots.
#   - Prints a compact line to stdout and mirrors parsed key/values to the log.
# =============================================================================

from __future__ import annotations

import argparse
import sys
import time

from fi import settings
from fi.semio.transport import SerialConfig, SemTransport
from fi.semio.protocol import SemProtocol

try:
    from fi.log import EventLogger
except Exception:  # pragma: no cover
    from fi.log.events import EventLogger

from fi.core.injector import status


def main(argv=None):
    # ----------------------------- CLI parsing ------------------------------
    p = argparse.ArgumentParser(description="Status helper (one-shot or --watch).")
    p.add_argument("--watch", action="store_true", help="Continuously poll and print counters")
    p.add_argument("--interval", type=float, default=1.0, help="Seconds between polls when --watch")
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

        def one():
            s = status(proto, log)
            # Mirror parsed counters to log line-by-line for readability.
            for k, v in s.items():
                log.log_rx(f"{k} {v}")
            # Provide a compact stdout summary for interactive use.
            printable = " ".join(f"{k}={v}" for k, v in s.items())
            print(printable if printable else "<no counters seen>")

        if not args.watch:
            one()
        else:
            try:
                while True:
                    one()
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                pass

    finally:
        log.close()
        tr.close()


if __name__ == "__main__":
    sys.exit(main())

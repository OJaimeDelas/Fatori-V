# =============================================================================
# FATORI-V • FI Engine SEM Setup
# File: engine/sem_setup.py
# -----------------------------------------------------------------------------
# Helper functions to open the SEM serial transport and protocol wrapper.
#=============================================================================

from __future__ import annotations

from typing import Tuple

from fi import fi_settings as settings
from fi.semio.transport import SemTransport
from fi.semio.protocol import SemProtocol

from .config import Config
from .logging_setup import LogContext


def open_sem(cfg: Config, log_ctx: LogContext) -> Tuple[SemTransport, SemProtocol]:
    """
    Open the serial connection to the SEM IP and build the SemProtocol object.

    This function:
      - Instantiates SemTransport with the chosen device and baud.
      - Instantiates SemProtocol with the transport and SEM frequency.
      - Optionally can perform a "preflight" status check (later).

    Returns:
        (transport, protocol)
    """
    # NOTE: adjust timeout or keyword args to match your current SemTransport
    # constructor in semio/transport.py.
    transport = SemTransport(
        device=cfg.dev,
        baudrate=cfg.baud,
        timeout=getattr(settings, "SEM_SERIAL_TIMEOUT_S", 1.0),
    )

    # SEM frequency typically lives in fi_settings as SEM_FREQ_HZ.
    sem_freq_hz = getattr(settings, "SEM_FREQ_HZ", 100_000_000)

    # NOTE: signature may differ; adjust to your actual SemProtocol __init__.
    proto = SemProtocol(
        transport=transport,
        sem_freq_hz=sem_freq_hz,
    )

    # For Part 1 we don't implement preflight here. If your current
    # fault_injection.py already does a status check before arming,
    # you can move that logic into a helper here later.

    # Example of where you could log something:
    log_ctx.logger.info(f"Opened SEM transport on {cfg.dev} @ {cfg.baud} baud")

    return transport, proto

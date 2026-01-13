# =============================================================================
# FATORI-V • FI CLI Parsing
# File: cli/parser.py
# -----------------------------------------------------------------------------
# Argument parser for the FI console command line interface.
#=============================================================================

import argparse

from fi import fi_settings


def _add_serial_args(parser: argparse.ArgumentParser) -> None:
    """
    Add SEM serial-port related arguments to the parser.

    These control how the FI console talks to the SEM controller over UART.
    """
    parser.add_argument(
        "-d",
        "--dev",
        dest="dev",
        default=fi_settings.DEFAULT_SEM_DEVICE,
        help=(
            "Serial device used to talk to SEM "
            f"(default: {fi_settings.DEFAULT_SEM_DEVICE})"
        ),
    )

    parser.add_argument(
        "-b",
        "--baud",
        dest="baud",
        type=int,
        default=fi_settings.DEFAULT_SEM_BAUDRATE,
        help=(
            "Baudrate for the SEM serial link "
            f"(default: {fi_settings.DEFAULT_SEM_BAUDRATE})"
        ),
    )


def _add_profile_args(parser: argparse.ArgumentParser) -> None:
    """
    Add area/time profile selection arguments to the parser.

    Area profiles are responsible for building a TargetPool, and time profiles
    decide when injections should happen.
    """
    parser.add_argument(
        "--area",
        dest="area_profile",
        default=fi_settings.DEFAULT_AREA_PROFILE,
        help=(
            "Area profile to use for building the target pool "
            f"(default: {fi_settings.DEFAULT_AREA_PROFILE!r})"
        ),
    )

    parser.add_argument(
        "--area-args",
        dest="area_args",
        default=fi_settings.DEFAULT_AREA_ARGS,
        help=(
            "Opaque argument string passed to the area profile "
            f"(default: {fi_settings.DEFAULT_AREA_ARGS!r})"
        ),
    )

    parser.add_argument(
        "--time",
        dest="time_profile",
        default=fi_settings.DEFAULT_TIME_PROFILE,
        help=(
            "Time profile to use for scheduling injections "
            f"(default: {fi_settings.DEFAULT_TIME_PROFILE!r})"
        ),
    )

    parser.add_argument(
        "--time-args",
        dest="time_args",
        default=fi_settings.DEFAULT_TIME_ARGS,
        help=(
            "Opaque argument string passed to the time profile "
            f"(default: {fi_settings.DEFAULT_TIME_ARGS!r})"
        ),
    )


def _add_dict_and_pool_args(parser: argparse.ArgumentParser) -> None:
    """
    Add system-dictionary and pool-file arguments to the parser.

    The system dictionary YAML describes the static structure of the system,
    while the optional pool file can pre-seed the TargetPool.
    """
    parser.add_argument(
        "--system-dict",
        dest="system_dict_path",
        default=fi_settings.SYSTEM_DICT_DEFAULT_PATH,
        help=(
            "Path to the system dictionary YAML file describing the board, "
            "modules, registers and pblocks "
            f"(default: {fi_settings.SYSTEM_DICT_DEFAULT_PATH!r})"
        ),
    )

    parser.add_argument(
        "--pool-file",
        dest="pool_file_path",
        default=fi_settings.INJECTION_POOL_DEFAULT_PATH,
        help=(
            "Optional path to an injection pool file. When provided, this is "
            "used to pre-seed the TargetPool. "
            f"(default: {fi_settings.INJECTION_POOL_DEFAULT_PATH!r})"
        ),
    )


def _add_board_and_acme_args(parser: argparse.ArgumentParser) -> None:
    """
    Add board-selection and ACME/EBD related arguments.

    These control how the ACME backend is configured:
      * which board model to use, and
      * where to find the EBD file describing the device configuration.
    """
    parser.add_argument(
        "--board",
        dest="board",
        default=None,
        help=(
            "Logical board name for ACME and system dictionary resolution "
            "(for example 'basys3' or 'xcku040'). If not provided, FI will "
            "attempt to use the board specified in the system dictionary, "
            "or fall back to a built-in default."
        ),
    )

    parser.add_argument(
        "--ebd-path",
        dest="ebd_path",
        default=fi_settings.DEFAULT_EBD_PATH,
        help=(
            "Path to the EBD file used by ACME to map regions to "
            f"configuration bits (default: {fi_settings.DEFAULT_EBD_PATH!r})"
        ),
    )


def _add_logging_args(parser: argparse.ArgumentParser) -> None:
    """
    Add high-level logging and output-directory arguments.

    The exact mapping from these arguments to log directories and filenames is
    handled by the logging setup module.
    """
    parser.add_argument(
        "--log-root",
        dest="log_root",
        default=fi_settings.LOG_ROOT,
        help=(
            "Base directory for FI logs. The logging setup module will create "
            "subdirectories beneath this root if USE_RUN_SUBDIRS is enabled. "
            f"(default: {fi_settings.LOG_ROOT!r})"
        ),
    )


def _add_gpio_args(parser: argparse.ArgumentParser) -> None:
    """
    Add GPIO configuration arguments to the parser.

    These arguments control the board interface for register-level
    fault injection via GPIO pins.
    """
    gpio_group = parser.add_argument_group(
        "GPIO Configuration",
        "Options for register injection via GPIO pins"
    )

    gpio_group.add_argument(
        "--gpio-enabled",
        action="store_true",
        help="Enable actual GPIO control (default: NoOp mode)"
    )

    gpio_group.add_argument(
        "--gpio-pin-start",
        type=int,
        default=None,
        help=f"Starting GPIO pin number for reg_id encoding (default: {fi_settings.REG_GPIO_PIN_START})"
    )

    gpio_group.add_argument(
        "--gpio-pin-count",
        type=int,
        default=None,
        help=f"Number of GPIO pins for reg_id encoding (default: {fi_settings.REG_GPIO_PIN_COUNT})"
    )

    gpio_group.add_argument(
        "--gpio-trigger-pin",
        type=int,
        default=None,
        help=f"GPIO pin number for injection trigger (default: {fi_settings.REG_GPIO_TRIGGER_PIN})"
    )

    gpio_group.add_argument(
        "--gpio-device",
        type=str,
        default=None,
        help=f"GPIO device path (default: {fi_settings.REG_GPIO_DEVICE_PATH})"
    )


def _add_seed_args(parser: argparse.ArgumentParser) -> None:
    """
    Add seed arguments for reproducibility.
    
    Seeds control random behavior in area and time profiles, allowing
    campaigns to be fully reproducible when the same seed is used.
    
    Seed resolution:
    - global-seed: Master seed that derives area-seed and time-seed
    - area-seed: Explicit override for area profile seed
    - time-seed: Explicit override for time profile seed
    
    If no seeds specified, random seeds are used (non-reproducible).
    """
    seed_group = parser.add_argument_group(
        "Seeds (Reproducibility)",
        "Control random behavior for reproducible campaigns"
    )
    
    seed_group.add_argument(
        "--global-seed",
        type=int,
        default=None,
        help=(
            "Master seed for campaign. Area and time seeds will be derived "
            "from this unless explicitly overridden."
        )
    )
    
    seed_group.add_argument(
        "--area-seed",
        type=int,
        default=None,
        help=(
            "Explicit seed for area profile. Overrides global-seed derivation. "
            "Controls target selection order."
        )
    )
    
    seed_group.add_argument(
        "--time-seed",
        type=int,
        default=None,
        help=(
            "Explicit seed for time profile. Overrides global-seed derivation. "
            "Controls injection timing randomness."
        )
    )


def build_arg_parser() -> argparse.ArgumentParser:
    """
    Construct and return the FI console argument parser.

    This parser intentionally only exposes user-facing knobs. The defaults for
    these knobs come from fi_settings, so changing a default in one place keeps
    the CLI and the rest of the system in sync.
    """
    parser = argparse.ArgumentParser(
        prog="fi",
        description="FATORI-V Fault Injection console",
    )

    _add_serial_args(parser)
    _add_profile_args(parser)
    _add_dict_and_pool_args(parser)
    _add_board_and_acme_args(parser)
    _add_logging_args(parser)
    _add_gpio_args(parser)
    _add_seed_args(parser)

    return parser


def parse_args(argv=None) -> argparse.Namespace:
    """
    Parse command-line arguments into an argparse.Namespace.

    The optional argv parameter is present to ease testing: when None, arguments
    are taken from sys.argv; otherwise, the provided iterable is used.
    """
    parser = build_arg_parser()
    return parser.parse_args(argv)
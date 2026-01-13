# =============================================================================
# FATORI-V • FI Engine Config
# File: engine/config.py
# -----------------------------------------------------------------------------
# Configuration container built from parsed CLI arguments.
#=============================================================================

from dataclasses import dataclass
from typing import Optional

from fi import fi_settings


@dataclass
class Config:
    """
    Simple container for FI runtime configuration.

    This object is intentionally kept as a dumb data holder: it does not contain
    any complex logic. All decisions (such as how to interpret board names or
    where to store logs) are made by the engine modules that consume it.
    """

    # Serial / SEM configuration.
    dev: str
    baud: int

    # Area/time profile selection and their opaque argument strings.
    area_profile: str
    area_args: Optional[str]
    time_profile: str
    time_args: Optional[str]

    # File-based inputs.
    system_dict_path: Optional[str]
    pool_file_path: Optional[str]

    # Logging root override (None means "use fi_settings.LOG_ROOT").
    log_root_override: Optional[str]

    # Board and ACME/EBD configuration.
    #
    # board_name can be provided explicitly through the CLI, or inferred from
    # the system dictionary. ebd_path points to the EBD file used by ACME.
    board_name: Optional[str]
    ebd_path: Optional[str]

    # GPIO configuration for register injection
    gpio_enabled: bool = False
    gpio_pin_start: int = 0
    gpio_pin_count: int = 8
    gpio_trigger_pin: int = 8
    gpio_device_path: str = "/dev/gpiochip0"

    # Seeds for reproducibility
    global_seed: Optional[int] = None
    area_seed: Optional[int] = None
    time_seed: Optional[int] = None


def build_config(args) -> Config:
    """
    Build a Config instance from the parsed CLI arguments.

    The goal is to copy values from the argparse Namespace into a structured
    dataclass without adding new defaulting logic here. Defaults should remain
    centralised in fi_settings and the CLI parser.
    """
    # Normalise empty strings to None for optional paths and argument strings.
    system_dict_path = args.system_dict_path or fi_settings.SYSTEM_DICT_DEFAULT_PATH
    pool_file_path = args.pool_file_path or None
    area_args = args.area_args or None
    time_args = args.time_args or None
    log_root_override = args.log_root or None
    board_name = args.board or None
    ebd_path = args.ebd_path or fi_settings.DEFAULT_EBD_PATH

    # GPIO configuration (use CLI args or fall back to settings)
    gpio_enabled = getattr(args, 'gpio_enabled', fi_settings.REG_GPIO_ENABLED)
    gpio_pin_start = getattr(args, 'gpio_pin_start', None)
    if gpio_pin_start is None:
        gpio_pin_start = fi_settings.REG_GPIO_PIN_START
    gpio_pin_count = getattr(args, 'gpio_pin_count', None)
    if gpio_pin_count is None:
        gpio_pin_count = fi_settings.REG_GPIO_PIN_COUNT
    gpio_trigger_pin = getattr(args, 'gpio_trigger_pin', None)
    if gpio_trigger_pin is None:
        gpio_trigger_pin = fi_settings.REG_GPIO_TRIGGER_PIN
    gpio_device_path = getattr(args, 'gpio_device', None)
    if gpio_device_path is None:
        gpio_device_path = fi_settings.REG_GPIO_DEVICE_PATH

    # Seed configuration
    global_seed = getattr(args, 'global_seed', None)
    area_seed = getattr(args, 'area_seed', None)
    time_seed = getattr(args, 'time_seed', None)

    cfg = Config(
        dev=args.dev,
        baud=int(args.baud),
        area_profile=args.area_profile,
        area_args=area_args,
        time_profile=args.time_profile,
        time_args=time_args,
        system_dict_path=system_dict_path,
        pool_file_path=pool_file_path,
        log_root_override=log_root_override,
        board_name=board_name,
        ebd_path=ebd_path,
        gpio_enabled=gpio_enabled,
        gpio_pin_start=gpio_pin_start,
        gpio_pin_count=gpio_pin_count,
        gpio_trigger_pin=gpio_trigger_pin,
        gpio_device_path=gpio_device_path,
        global_seed=global_seed,
        area_seed=area_seed,
        time_seed=time_seed,
    )

    return cfg
# =============================================================================
# FATORI-V • FI Profile Loader
# File: profile_loader.py
# -----------------------------------------------------------------------------
# Resolves area/time profile names into live profile objects.
#
# Profiles live under:
#   - fi/profiles/area/<name>.py
#   - fi/profiles/time/<name>.py
#
# Each profile module must expose:
#   - PROFILE_KIND: "area" or "time"
#   - PROFILE_NAME: short string (usually module name)
#   - describe()   -> str
#   - default_args() -> dict[str, Any]
#   - make_profile(args: dict[str, Any], *, global_seed: int | None, settings)
#
# Area profiles return objects with:
#   - next_target() -> TargetSpec | None
#   - describe()    -> str
#
# Time profiles return objects with:
#   - run(controller) -> None
#
# This loader parses the CSV "k=v,k2=v2" argument strings from Config and
# calls make_profile(...) with a dict of parsed values.
#=============================================================================

from __future__ import annotations

import importlib
from typing import Any, Dict

from fi import fi_settings as settings
from fi.engine.config import Config
from fi.engine.seed_manager import (
    get_effective_seed,
    derive_area_seed,
    derive_time_seed
)


# ----------------------------------------------------------------------------- 
# Helper: parse "k=v,k2=v2" argument strings into dictionaries
# ----------------------------------------------------------------------------- 
def _parse_arg_csv(csv: str) -> Dict[str, str]:
    """
    Parse a simple comma-separated "k=v" list into a dictionary.

    Examples:
        "path=addresses.txt,order=sequential"
        "rate_hz=5,duration_s=60"

    Whitespace around keys and values is stripped. Empty strings map to {}.
    """
    result: Dict[str, str] = {}
    if not csv:
        return result

    parts = csv.split(",")
    for raw in parts:
        item = raw.strip()
        if not item:
            # Skip empty segments
            continue
        if "=" not in item:
            # Bare flag: treat as key with value "true"
            result[item] = "true"
            continue
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            # Ignore malformed pieces without a key
            continue
        result[key] = value
    return result


# ----------------------------------------------------------------------------- 
# Internal loader for profile modules
# ----------------------------------------------------------------------------- 
def _load_profile_module(kind: str, name: str):
    """
    Import the Python module that implements a given profile.

    kind:
        "area" or "time".
    name:
        logical profile name (e.g. "address_list", "uniform").

    The module is expected at:
        fi.profiles.<kind>.<name>
    """
    if not name:
        raise ValueError(f"Profile name for kind '{kind}' is empty.")

    module_path = f"fi.profiles.{kind}.{name}"
    return importlib.import_module(module_path)


def _build_profile(
    kind: str,
    name: str,
    args_csv: str,
    cfg: Config,
) -> Any:
    """
    Shared builder for both area and time profiles.

    kind:
        "area" or "time".
    name:
        profile name, used as module name under fi.profiles.
    args_csv:
        CSV "k=v" string from Config (area_args or time_args).
    cfg:
        full configuration object (seed fields used here).
    """
    module = _load_profile_module(kind, name)

    # Sanity check the advertised kind, when present.
    advertised_kind = getattr(module, "PROFILE_KIND", None)
    if advertised_kind is not None and advertised_kind != kind:
        raise RuntimeError(
            f"Profile '{name}' claims kind '{advertised_kind}' "
            f"but was requested as '{kind}'."
        )

    # Parse arguments string into a dict.
    args_dict = _parse_arg_csv(args_csv)

    # Every profile module must expose make_profile.
    factory = getattr(module, "make_profile", None)
    if factory is None:
        raise RuntimeError(
            f"Profile module 'fi.profiles.{kind}.{name}' does not "
            f"define make_profile(...)."
        )

    # Derive effective seed based on kind
    if kind == "area":
        effective_seed = get_effective_seed(
            explicit=cfg.area_seed,
            global_seed=cfg.global_seed,
            derive_fn=derive_area_seed
        )
    elif kind == "time":
        effective_seed = get_effective_seed(
            explicit=cfg.time_seed,
            global_seed=cfg.global_seed,
            derive_fn=derive_time_seed
        )
    else:
        # Fallback for unknown kinds (should not happen)
        effective_seed = cfg.global_seed

    profile = factory(
        args=args_dict,
        global_seed=effective_seed,
        settings=settings,
    )
    return profile


# ----------------------------------------------------------------------------- 
# Public helpers used by the FI engine
# ----------------------------------------------------------------------------- 
def load_area_profile(cfg: Config):
    """
    Load and construct the area profile selected in the Config.

    The resulting object is expected to expose at least:
        - next_target() -> TargetSpec | None
        - describe()    -> str
    
    Seed resolution:
    1. Explicit --area-seed takes priority
    2. Derived from --global-seed if present
    3. No seed (profile uses random)
    """
    name = cfg.area_profile
    args_csv = cfg.area_args
    return _build_profile("area", name, args_csv, cfg)


def load_time_profile(cfg: Config):
    """
    Load and construct the time profile selected in the Config.

    The resulting object is expected to expose:
        - run(controller) -> None
    where `controller` is an InjectionController instance.
    
    Seed resolution:
    1. Explicit --time-seed takes priority
    2. Derived from --global-seed if present
    3. No seed (profile uses random)
    """
    name = cfg.time_profile
    args_csv = cfg.time_args
    return _build_profile("time", name, args_csv, cfg)
# =============================================================================
# FATORI-V • CLI Style Banners
# File: banners.py
# -----------------------------------------------------------------------------
# Helpers for printing consistent CLI banners and run headers/footers.
#=============================================================================

from __future__ import annotations

from typing import Iterable, Tuple

from scripts.common import common_settings as cset


def _line(char: str = "#", width: int | None = None) -> str:
    """
    Build a single-line separator using the given character and width.
    """
    if width is None:
        width = cset.CLI_LINE_WIDTH
    return char * width

def _colour(text: str, colour_code: str) -> str:
    """
    Wrap text in ANSI colour codes if colour output is enabled.
    """
    if not cset.USE_COLOUR_OUTPUT:
        return text
    if not colour_code:
        return text
    return f"{colour_code}{text}{cset.COLOR_RESET}"


def print_main_banner(run_previews: Iterable[Tuple[str, str]]) -> None:
    """
    Print the top-level banner and the list of runs that will execute.

    Args:
        run_previews: Iterable of (run_name, yaml_filename) pairs.
    """
    width = cset.CLI_LINE_WIDTH

    sep_plain = _line("#", width)
    sep = _colour(sep_plain, cset.MAIN_HEADER_LINE_COLOR)
    title = _colour("#", cset.MAIN_HEADER_LINE_COLOR) +  _colour("F A T O R I  -  V".center(width-2), cset.MAIN_TITLE_COLOR) + _colour("#", cset.MAIN_HEADER_LINE_COLOR)

    print(sep)
    print(title)
    print(sep)
    print()

    print("Runs that will execute:")
    for name, fname in run_previews:
        print(f"  - {name}  (from {fname})")
    print()


def print_run_header(
    run_id: str,
    yaml_filename: str,
    area_profile: str,
    time_profile: str,
    seed: int,
) -> None:
    """
    Print a short header at the start of each run.

    Args:
        run_id:        Logical identifier of the run.
        yaml_filename: Name of the YAML file (for reference).
        area_profile:  Name of the FI area profile.
        time_profile:  Name of the FI time profile.
        seed:          Global seed chosen for this run.
    """
    width = cset.CLI_LINE_WIDTH

    sep_plain = _line("#", width)
    sep = _colour(sep_plain, cset.RUN_HEADER_LINE_COLOR)
    title = _colour(f" NEW RUN: {run_id} ".center(width, "#"), cset.RUN_TITLE_COLOR)

    print()
    print(sep)
    print(title)
    print(sep)
    print(f"YAML file    : {yaml_filename}")
    print(f"Area profile : {area_profile}")
    print(f"Time profile : {time_profile}")
    print(f"Global seed  : {seed}")
    print()



def print_run_footer(run_id: str) -> None:
    """
    Print a short footer at the end of each run.

    Args:
        run_id: Logical identifier of the run.
    """
    width = cset.CLI_LINE_WIDTH

    sep_plain = _line("#", width)
    sep = _colour(sep_plain, cset.RUN_HEADER_LINE_COLOR)
    title = _colour(f" END OF RUN: {run_id} ".center(width, "#"), cset.RUN_TITLE_COLOR)

    print()
    print(sep)
    print(title)
    print(sep)
    print()
# =============================================================================
# FATORI-V • Reports • Vivado Parser Caller
# File: vivado_parser_caller.py
# -----------------------------------------------------------------------------
# Calls external Vivado report parser system.
# =============================================================================

import sys
from pathlib import Path


def call_parser(reports_dir: Path, prefix: str, output_dir: Path) -> int:
    """
    Call Vivado report parser.
    
    Args:
        reports_dir: Directory containing Vivado reports
        prefix: Common prefix of report files
        output_dir: Output directory for parsed metrics
    
    Returns:
        Exit code (0 = success, 1 = error)
    """
    # Add parser to path
    parser_dir = Path(__file__).parent / "parser"
    if str(parser_dir) not in sys.path:
        sys.path.insert(0, str(parser_dir))
    
    # Import parser main function
    try:
        from vivado_report_system import main as parse_reports
    except ImportError as e:
        print(f"Error: Could not import parser system: {e}")
        print(f"Expected parser at: {parser_dir}")
        return 1
    
    # Ensure paths are strings
    reports_dir = str(reports_dir)
    output_dir = str(output_dir)
    
    # Call parser main function
    try:
        result = parse_reports(reports_dir, prefix, output_dir)
        return result if result is not None else 0
    except Exception as e:
        print(f"Error calling report parser: {e}")
        return 1


if __name__ == "__main__":
    # CLI interface for standalone testing
    if len(sys.argv) < 4:
        print("Usage: python vivado_parser_caller.py <reports_dir> <prefix> <output_dir>")
        sys.exit(1)
    
    reports_dir = Path(sys.argv[1])
    prefix = sys.argv[2]
    output_dir = Path(sys.argv[3])
    
    exit_code = call_parser(reports_dir, prefix, output_dir)
    sys.exit(exit_code)
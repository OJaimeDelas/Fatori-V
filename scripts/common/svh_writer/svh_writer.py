# =============================================================================
# FATORI-V • Common Utilities • SVH Writer
# File: svh_writer.py
# -----------------------------------------------------------------------------
# Generates properly formatted SystemVerilog header files with include guards.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from config.constants import HEADER_WIDTH, INDENT_SPACES


def generate_svh_header(file_name, description, area="Common"):
    """
    Generate a standard FATORI-V header comment block for SVH files.
    
    Args:
        file_name: Name of the file (e.g., "fatori_features.svh")
        description: One-line description of the file's purpose
        area: Functional area (e.g., "Features", "FTM", "Pblocks")
    
    Returns:
        String containing the formatted header comment
    """
    lines = []
    
    # Top separator line
    lines.append("//" + "=" * (HEADER_WIDTH - 1))
    
    # Title line
    title = f"FATORI-V • {area}"
    lines.append(f"// {title}")
    
    # File line
    lines.append(f"// File: {file_name}")
    
    # Sub-separator line
    lines.append("//" + "-" * (HEADER_WIDTH - 2))
    
    # Description line
    lines.append(f"// {description}")
    
    # Bottom separator line
    lines.append("//" + "=" * (HEADER_WIDTH - 1))
    
    return "\n".join(lines)


def generate_include_guard_start(file_name):
    """
    Generate the opening of an include guard for an SVH file.
    
    Args:
        file_name: Name of the file (e.g., "fatori_features.svh")
    
    Returns:
        String containing the ifndef and define directives
    """
    # Convert filename to guard name: fatori_features.svh -> FATORI_FEATURES_SVH
    guard_name = file_name.upper().replace(".", "_")
    
    lines = [
        f"`ifndef {guard_name}",
        f"`define {guard_name}"
    ]
    
    return "\n".join(lines)


def generate_include_guard_end(file_name):
    """
    Generate the closing of an include guard for an SVH file.
    
    Args:
        file_name: Name of the file
    
    Returns:
        String containing the endif directive with comment
    """
    guard_name = file_name.upper().replace(".", "_")
    return f"`endif // {guard_name}"


def generate_section_comment(section_name):
    """
    Generate a section divider comment.
    
    Args:
        section_name: Name of the section (e.g., "ISA Extensions")
    
    Returns:
        String containing the formatted section comment
    """
    lines = []
    
    # Section separator
    lines.append("// " + "-" * (HEADER_WIDTH - 3))
    
    # Section name
    lines.append(f"// {section_name}")
    
    # Section separator
    lines.append("// " + "-" * (HEADER_WIDTH - 3))
    
    return "\n".join(lines)


def generate_macro_define(macro_name, value=None, comment=None):
    """
    Generate a macro define statement.
    
    Args:
        macro_name: Name of the macro (without prefix)
        value: Optional value for the macro. If None, just defines the macro
        comment: Optional inline comment explaining the macro
    
    Returns:
        String containing the define directive
    """
    # Build the define statement
    if value is None:
        define_str = f"`define {macro_name}"
    else:
        define_str = f"`define {macro_name} {value}"
    
    # Add comment if provided
    if comment:
        # Pad to ensure alignment
        padding = " " * max(1, 40 - len(define_str))
        define_str += f"{padding}// {comment}"
    
    return define_str


def generate_macro_undef(macro_name):
    """
    Generate a macro undef statement.
    
    Args:
        macro_name: Name of the macro to undefine
    
    Returns:
        String containing the undef directive
    """
    return f"`undef {macro_name}"


def generate_ifdef_block(condition, if_content, else_content=None):
    """
    Generate an ifdef conditional block.
    
    Args:
        condition: Macro name to test (without backtick)
        if_content: Content when condition is true (list of lines or string)
        else_content: Optional content when condition is false
    
    Returns:
        String containing the complete ifdef block
    """
    lines = []
    
    # Opening ifdef
    lines.append(f"`ifdef {condition}")
    
    # If content
    if isinstance(if_content, list):
        lines.extend(if_content)
    else:
        lines.append(if_content)
    
    # Optional else block
    if else_content:
        lines.append("`else")
        if isinstance(else_content, list):
            lines.extend(else_content)
        else:
            lines.append(else_content)
    
    # Closing endif
    lines.append("`endif")
    
    return "\n".join(lines)


def generate_include_statement(file_name):
    """
    Generate an include statement for another SVH file.
    
    Args:
        file_name: Name of the file to include
    
    Returns:
        String containing the include directive
    """
    return f'`include "{file_name}"'


def indent(text, level=1):
    """
    Indent text by a specified number of levels.
    
    Args:
        text: Text to indent (can be multi-line string)
        level: Number of indent levels (each level = INDENT_SPACES spaces)
    
    Returns:
        Indented text
    """
    spaces = " " * (cfg.INDENT_SPACES * level)
    
    if "\n" in text:
        # Multi-line text: indent each line
        lines = text.split("\n")
        return "\n".join(spaces + line if line.strip() else line for line in lines)
    else:
        # Single line
        return spaces + text


def write_svh_file(output_path, file_name, description, content, area="Common", includes=None):
    """
    Write a complete SVH file with proper structure.
    
    This function assembles all the components:
    - Header comment
    - Include guard start
    - Include statements (if any)
    - Content
    - Include guard end
    
    Args:
        output_path: Directory where file should be written
        file_name: Name of the SVH file
        description: One-line description for the header
        content: Main content of the file (list of lines or string)
        area: Functional area for the header
        includes: Optional list of files to include
    
    Returns:
        Path object for the created file
    """
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    file_path = output_path / file_name
    
    lines = []
    
    # File header
    lines.append(generate_svh_header(file_name, description, area))
    lines.append("")
    
    # Include guard start
    lines.append(generate_include_guard_start(file_name))
    lines.append("")
    
    # Include statements if provided
    if includes:
        for include_file in includes:
            lines.append(generate_include_statement(include_file))
        lines.append("")
    
    # Main content
    if isinstance(content, list):
        lines.extend(content)
    else:
        lines.append(content)
    
    lines.append("")
    
    # Include guard end
    lines.append(generate_include_guard_end(file_name))
    
    # Write to file
    with file_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        f.write("\n")  # Ensure file ends with newline
    
    return file_path
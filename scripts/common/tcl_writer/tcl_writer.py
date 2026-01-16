# =============================================================================
# FATORI-V • Common Utilities • TCL Writer
# File: tcl_writer.py
# -----------------------------------------------------------------------------
# Generates properly formatted TCL scripts for Vivado.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from config.constants import HEADER_WIDTH, INDENT_SPACES


def generate_tcl_header(file_name, description, purpose="Vivado Script"):
    """
    Generate a standard FATORI-V header comment block for TCL files.
    
    Args:
        file_name: Name of the file (e.g., "pre_synthesis.tcl")
        description: One-line description of the script's purpose
        purpose: Type of script (e.g., "Pre-Synthesis", "Post-Opt")
    
    Returns:
        String containing the formatted header comment
    """
    lines = []
    
    # Top separator line
    lines.append("#" + "=" * (HEADER_WIDTH - 1))
    
    # Title line
    title = f"FATORI-V • {purpose}"
    lines.append(f"# {title}")
    
    # File line
    lines.append(f"# File: {file_name}")
    
    # Sub-separator line
    lines.append("#" + "-" * (HEADER_WIDTH - 1))
    
    # Description line
    lines.append(f"# {description}")
    
    # Bottom separator line
    lines.append("#" + "=" * (HEADER_WIDTH - 1))
    
    return "\n".join(lines)


def generate_section_comment(section_name):
    """
    Generate a section divider comment for TCL scripts.
    
    Args:
        section_name: Name of the section
    
    Returns:
        String containing the formatted section comment
    """
    lines = []
    
    # Section separator
    lines.append("# " + "-" * (HEADER_WIDTH - 2))
    
    # Section name
    lines.append(f"# {section_name}")
    
    # Section separator
    lines.append("# " + "-" * (HEADER_WIDTH - 2))
    
    return "\n".join(lines)


def generate_comment(text, inline=False):
    """
    Generate a comment line or inline comment.
    
    Args:
        text: Comment text
        inline: If True, returns comment suitable for appending to a line
    
    Returns:
        String containing the formatted comment
    """
    if inline:
        return f" ;# {text}"
    else:
        return f"# {text}"


def generate_puts_statement(message, colored=False):
    """
    Generate a puts statement for console output.
    
    Args:
        message: Message to print
        colored: If True, use Vivado color formatting (not implemented yet)
    
    Returns:
        String containing the puts statement
    """
    # Escape special characters in message
    escaped = message.replace('"', '\\"').replace('\\', '\\\\')
    
    return f'puts "{escaped}"'


def generate_source_statement(file_path):
    """
    Generate a source statement to include another TCL file.
    
    Args:
        file_path: Path to the TCL file to source
    
    Returns:
        String containing the source statement
    """
    return f'source "{file_path}"'


def generate_set_statement(var_name, value):
    """
    Generate a set statement for variable assignment.
    
    Args:
        var_name: Name of the variable
        value: Value to assign (will be properly formatted)
    
    Returns:
        String containing the set statement
    """
    # Handle different value types
    if isinstance(value, bool):
        # Boolean: convert to 1/0
        tcl_value = "1" if value else "0"
    elif isinstance(value, str):
        # String: quote it
        tcl_value = f'"{value}"'
    elif isinstance(value, (list, tuple)):
        # List: convert to TCL list format
        items = [f'"{item}"' if isinstance(item, str) else str(item) for item in value]
        tcl_value = "{" + " ".join(items) + "}"
    else:
        # Number: use as-is
        tcl_value = str(value)
    
    return f"set {var_name} {tcl_value}"


def generate_if_block(condition, if_body, else_body=None):
    """
    Generate an if conditional block.
    
    Args:
        condition: Condition to test (as TCL expression)
        if_body: Body when condition is true (list of lines or string)
        else_body: Optional body when condition is false
    
    Returns:
        String containing the complete if block
    """
    lines = []
    
    # Opening if with opening brace
    lines.append(f"if {{{condition}}} {{")
    
    # If body (indented)
    if isinstance(if_body, list):
        for line in if_body:
            lines.append(indent(line))
    else:
        lines.append(indent(if_body))
    
    # Optional else block
    if else_body:
        lines.append("} else {")
        if isinstance(else_body, list):
            for line in else_body:
                lines.append(indent(line))
        else:
            lines.append(indent(else_body))
    
    # Closing brace
    lines.append("}")
    
    return "\n".join(lines)


def generate_foreach_loop(var_name, list_expr, body):
    """
    Generate a foreach loop.
    
    Args:
        var_name: Loop variable name
        list_expr: Expression that evaluates to a list
        body: Loop body (list of lines or string)
    
    Returns:
        String containing the complete foreach loop
    """
    lines = []
    
    # Opening foreach with opening brace
    lines.append(f"foreach {var_name} {list_expr} {{")
    
    # Loop body (indented)
    if isinstance(body, list):
        for line in body:
            lines.append(indent(line))
    else:
        lines.append(indent(body))
    
    # Closing brace
    lines.append("}")
    
    return "\n".join(lines)


def generate_proc_definition(proc_name, args, body, description=None):
    """
    Generate a procedure definition.
    
    Args:
        proc_name: Name of the procedure
        args: List of argument names
        body: Procedure body (list of lines or string)
        description: Optional description comment
    
    Returns:
        String containing the complete proc definition
    """
    lines = []
    
    # Optional description comment
    if description:
        lines.append(generate_comment(description))
    
    # Proc header with arguments
    args_str = " ".join(args) if args else ""
    lines.append(f"proc {proc_name} {{{args_str}}} {{")
    
    # Proc body (indented)
    if isinstance(body, list):
        for line in body:
            lines.append(indent(line))
    else:
        lines.append(indent(body))
    
    # Closing brace
    lines.append("}")
    
    return "\n".join(lines)


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


def write_tcl_file(output_path, file_name, description, content, purpose="Vivado Script"):
    """
    Write a complete TCL file with proper structure.
    
    This function assembles all the components:
    - Header comment
    - Content
    
    Args:
        output_path: Directory where file should be written
        file_name: Name of the TCL file
        description: One-line description for the header
        content: Main content of the file (list of lines or string)
        purpose: Purpose/type of script for the header
    
    Returns:
        Path object for the created file
    """
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    file_path = output_path / file_name
    
    lines = []
    
    # File header
    lines.append(generate_tcl_header(file_name, description, purpose))
    lines.append("")
    
    # Main content
    if isinstance(content, list):
        lines.extend(content)
    else:
        lines.append(content)
    
    # Write to file
    with file_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        f.write("\n")  # Ensure file ends with newline
    
    return file_path
# launch.py

"""
Cross-platform launcher for GenericAgent.

This script delegates to `launch.pyw`, ensuring that the agent launches
consistently across different operating systems. On Windows, it will use
`pythonw.exe` when available to hide the console window; on other
platforms it simply invokes the same Python interpreter that is running
this script.

Any additional command-line arguments provided to this script will be
forwarded to `launch.pyw` unchanged.
"""

from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path
import platform


def main() -> None:
    """Entry point for the cross-platform launcher."""
    script_dir = Path(__file__).resolve().parent
    target = script_dir / "launch.pyw"
    python_executable = sys.executable or "python"

    # Prefer pythonw.exe on Windows to avoid showing a console window.
    if platform.system() == "Windows":
        exe_lower = python_executable.lower()
        if exe_lower.endswith("python.exe"):
            candidate = python_executable[:-len("python.exe")] + "pythonw.exe"
            if os.path.exists(candidate):
                python_executable = candidate

    # Build command to run launch.pyw with any extra args passed to this script
    cmd = [python_executable, str(target)] + sys.argv[1:]
    # Execute without raising exceptions on non-zero exit codes
    subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()

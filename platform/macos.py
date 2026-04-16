# platform/macos.py

"""
macOS-specific platform adapter implementation.

This module provides the `MacOSAdapter` class, which inherits from
`PlatformAdapter` and implements methods suitable for macOS systems,
including detection of the default shell, definition of the workspace
root, and identification of sensitive paths.

Both Intel and Apple Silicon Macs share similar filesystem layouts and
permission models, so this adapter applies to both architectures. If
different behavior is required for Apple Silicon in the future, it can
be subclassed further.
"""

from __future__ import annotations

import os
from pathlib import Path

from .base import PlatformAdapter

class MacOSAdapter(PlatformAdapter):
    """Platform adapter implementation for macOS systems."""

    def get_default_shell(self) -> list[str]:
        """Return the default shell command for macOS.

        On macOS, the user's login shell is typically `/bin/zsh` or `/bin/bash`.
        This method returns a command list to execute commands via the login
        shell with the `-lc` flag, ensuring that login scripts are sourced
        before running any commands. If the `SHELL` environment variable is
        set, it is used; otherwise it falls back to `/bin/zsh`.
        """
        shell = os.environ.get("SHELL", "/bin/zsh")
        return [shell, "-lc"]

    def get_workspace_root(self) -> str:
        """Return the default workspace root for the agent on macOS.

        By convention this implementation uses a folder named
        `GenericAgentWorkspace` in the user's home directory. The caller
        is responsible for creating the directory if it does not exist.
        """
        home = Path.home()
        return str(home / "GenericAgentWorkspace")

    def get_sensitive_paths(self) -> list[str]:
        """Return a list of sensitive directories on macOS.

        These paths correspond to system or user directories where
        modifications could harm the operating system or compromise
        security. The policy engine should require confirmation or deny
        operations that attempt to modify files in these paths.
        """
        home = Path.home()
        return [
            "/System",
            "/Library",
            "/Applications",
            str(home / "Library"),
            str(home / ".ssh"),
        ]

    def requires_accessibility_permission(self) -> bool:
        """Indicate that macOS requires accessibility permission for automation."""
        return True

    def requires_screen_recording_permission(self) -> bool:
        """Indicate that macOS may require screen recording permission for capture."""
        return True

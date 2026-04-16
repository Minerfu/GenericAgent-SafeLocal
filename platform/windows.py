# platform/windows.py

"""
Windows-specific platform adapter implementation.

This module provides the `WindowsAdapter` class, which inherits from
`PlatformAdapter` and supplies sensible defaults for running on the
Windows operating system. It specifies the default shell, workspace
location, and directories that should be considered sensitive.
"""

from __future__ import annotations

import os
from pathlib import Path

from .base import PlatformAdapter

class WindowsAdapter(PlatformAdapter):
    """Platform adapter implementation for Windows systems."""

    def get_default_shell(self) -> list[str]:
        """Return the default shell command for Windows.

        On Windows, the simplest shell invocation is via `cmd` with the
        `/c` flag to execute a command and then terminate. Alternatively,
        PowerShell could be used, but cmd.exe is sufficient for many
        internal tasks and avoids needing to load the PowerShell engine.
        """
        return ["cmd", "/c"]

    def get_workspace_root(self) -> str:
        """Return the default workspace root for Windows.

        By default this implementation uses a directory on the system
        drive called `GenericAgentWorkspace`. If the `SystemDrive`
        environment variable is not set, it falls back to the current
        user's home directory.
        """
        drive = os.environ.get("SystemDrive")
        if drive:
            return os.path.join(drive + "\\", "GenericAgentWorkspace")
        # Fallback to home directory
        return str(Path.home() / "GenericAgentWorkspace")

    def get_sensitive_paths(self) -> list[str]:
        """Return a list of sensitive directories on Windows.

        These paths include Windows system folders and user profile
        directories that should be protected from modification by the
        agent unless explicitly approved.
        """
        return [
            "C:\\Windows",
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            os.path.expandvars("%APPDATA%"),
            os.path.expandvars("%LOCALAPPDATA%"),
            os.path.expandvars("%USERPROFILE%\\.ssh"),
        ]

    def requires_accessibility_permission(self) -> bool:
        """Windows does not have the same accessibility permission model."""
        return False

    def requires_screen_recording_permission(self) -> bool:
        """Windows does not typically require screen recording permission."""
        return False

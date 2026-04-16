platform/base.py  # platform/base.py

"""
Base definitions for platform-specific behaviors.

This module defines the `PlatformAdapter` class, which can be subclassed to
provide operating system-specific values for shells, workspaces, and sensitive
paths. It also exposes methods to declare whether certain permissions (like
accessibility or screen recording) are required for automation on the
platform.

These definitions are minimal and designed to be extended by specific
platform implementations.
"""

from __future__ import annotations

from pathlib import Path

class PlatformAdapter:
    """Base adapter class for platform-specific behaviours."""

    def get_default_shell(self) -> list[str]:
        """Return the default shell command as a list for subprocess calls.

        Subclasses should override this method to return a command list that
        can be passed to subprocess. For example, Windows might return
        ["cmd", "/c"], whereas UNIX-like systems could return ["/bin/bash", "-lc"].
        """
        raise NotImplementedError("PlatformAdapter.get_default_shell must be overridden")

    def get_workspace_root(self) -> str:
        """Return the workspace root path as a string.

        The returned path defines where the agent may read and write files by
        default. Subclasses should override this to specify a suitable
        location on the host operating system. For example, on Windows it
        could be something like C:\\GenericAgentWorkspace, and on macOS
        ~/GenericAgentWorkspace.
        """
        raise NotImplementedError("PlatformAdapter.get_workspace_root must be overridden")

    def get_sensitive_paths(self) -> list[str]:
        """Return a list of sensitive system paths.

        Sensitive paths are directories where modifications should be
        discouraged or require elevated approval. Examples include system
        directories like /System or C:\\Windows. Subclasses can extend
        this list as appropriate.
        """
        return []

    def requires_accessibility_permission(self) -> bool:
        """Whether the platform requires accessibility permissions.

        Some operating systems require explicit user consent (e.g. macOS
        Accessibility permissions) for programmatic control of the keyboard
        or mouse. Subclasses can override this to indicate if such
        permissions are necessary.
        """
        return False

    def requires_screen_recording_permission(self) -> bool:
        """Whether the platform requires screen recording permission.

        On macOS, capturing the screen may require the user to grant
        screen recording permissions. Subclasses can override this to
        indicate whether these permissions are needed.
        """
        return False

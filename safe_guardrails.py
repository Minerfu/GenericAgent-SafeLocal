import os, re
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List

class Decision(str, Enum):
    """Possible policy decisions for tool execution."""
    ALLOW = "allow"
    DENY = "deny"
    CONFIRM = "confirm"
    REWRITE = "rewrite"

@dataclass
class PolicyResult:
    """Result of evaluating a tool call."""
    decision: Decision
    reason: str = ""
    rewritten_args: Optional[Dict[str, Any]] = None
    risk: int = 0
    tags: List[str] = field(default_factory=list)

class SafePolicyEngine:
    """
    Evaluate tool invocations and decide whether to allow, deny, or require confirmation.
    This class encapsulates heuristics for detecting potentially dangerous actions.
    The heuristics here are minimal and intended to be extended.
    """

    # Patterns for commands that might be destructive if run without supervision
    DANGEROUS_COMMAND_PATTERNS = [
        r"\b(rm -rf|rm -r|del /s|erase)\b",
        r"\b(format|diskpart|mkfs)\b",
    ]

    # Paths that should not be touched without confirmation
    SENSITIVE_PATHS = [
        "/etc", "/boot", "C:\\Windows", "C:\\Program Files",
        os.path.expanduser("~/.ssh"),
    ]

    # Imports in Python that often lead to system-level access
    DANGEROUS_IMPORTS = {"subprocess", "shutil", "os", "socket", "winreg", "ctypes"}

    def is_within_workspace(self, path: str, workspace: str) -> bool:
        """Return True if path is within the allowed workspace."""
        try:
            abs_path = os.path.abspath(path)
            abs_workspace = os.path.abspath(workspace)
            return abs_path.startswith(abs_workspace)
        except Exception:
            return False

    def evaluate(self, tool_name: str, tool_args: Dict[str, Any], workspace: str = ".") -> PolicyResult:
        """Evaluate a tool call and return a PolicyResult."""
        # Filesystem operations: confirm if outside workspace
        if tool_name in ("file_read", "file_write", "file_patch"):
            path = tool_args.get("path") or tool_args.get("file")
            if path and not self.is_within_workspace(path, workspace):
                return PolicyResult(
                    decision=Decision.CONFIRM,
                    reason=f"Access to path {path} is outside the workspace",
                    tags=["filesystem"],
                )
        # Code execution: check for dangerous imports or patterns
        if tool_name == "code_run":
            script: str = tool_args.get("code", "") or tool_args.get("script", "")
            for imp in self.DANGEROUS_IMPORTS:
                if f"import {imp}" in script:
                    return PolicyResult(
                        decision=Decision.CONFIRM,
                        reason=f"Detected dangerous import '{imp}'",
                        tags=["code", "import"],
                    )
            for pat in self.DANGEROUS_COMMAND_PATTERNS:
                if re.search(pat, script, re.IGNORECASE):
                    return PolicyResult(
                        decision=Decision.CONFIRM,
                        reason=f"Detected risky command pattern matching '{pat}'",
                        tags=["code", "command"],
                    )
        # Browser or network actions could be handled here if needed
        return PolicyResult(decision=Decision.ALLOW)

class ExecutionBroker:
    """
    Wrap the actual tool execution behind a policy engine.
    The broker defers to a provided ask_user callable when user confirmation is required.
    This class does not execute anything itself; it delegates to the passed executor.
    """

    def __init__(self, policy_engine: SafePolicyEngine, ask_user_fn):
        self.policy_engine = policy_engine
        self.ask_user = ask_user_fn

    def run(self, tool_name: str, tool_args: Dict[str, Any], executor, workspace: str = "."):
        """Evaluate and possibly execute a tool call."""
        result = self.policy_engine.evaluate(tool_name, tool_args, workspace)
        if result.decision == Decision.DENY:
            return {"ok": False, "error": result.reason}
        elif result.decision == Decision.CONFIRM:
            # Ask the user for confirmation via ask_user tool. Expect True/False.
            question = (
                f"Tool {tool_name} requested with args {tool_args}. Reason: {result.reason}. Proceed?"
            )
            try:
                approved = self.ask_user(question)
            except Exception:
                approved = False
            if not approved:
                return {"ok": False, "error": "User denied execution."}
        # If allow or after confirmation, call executor
        return executor(tool_name, tool_args)

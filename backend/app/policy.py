import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .models import PolicyDecision, ToolCall


@dataclass
class PolicyEngine:
    max_tool_calls: int = 8
    registered_tools: dict[str, dict[str, Any]] = field(default_factory=dict)
    history: list[str] = field(default_factory=list)
    task_complete: bool = False

    def evaluate(self, call: ToolCall) -> list[PolicyDecision]:
        action = call.name
        decisions: list[PolicyDecision] = []
        decisions.append(self._decision("registered_tool", action, action in self.registered_tools,
                                        "Tool is registered." if action in self.registered_tools else "Tool is not registered."))

        if action not in self.registered_tools:
            return decisions

        args_text = json.dumps(call.arguments, sort_keys=True).lower()
        destructive = bool(re.search(r"\b(delete|destroy|terminate|purge|drop)\b", action.lower())) or bool(
            re.search(r"\b(delete|destroy|terminate|purge|drop)\b", args_text)
        )
        decisions.append(self._decision(
            "deny_destructive_actions", action, not destructive,
            "No destructive operation detected." if not destructive else "Destructive operations are disabled in the mock environment.",
        ))

        secret_or_unauthorized = bool(re.search(r"(secret|credential|\.env|id_rsa|/etc/|password)", args_text))
        decisions.append(self._decision(
            "authorized_arguments", action, not secret_or_unauthorized,
            "Arguments stay within the approved resource scope." if not secret_or_unauthorized else "Arguments reference a secret or unauthorized path.",
        ))

        valid_schema, schema_reason = self._validate_schema(action, call.arguments)
        decisions.append(self._decision("strict_argument_schema", action, valid_schema, schema_reason))

        repeated = action in self.history and self.history[-1] == action
        decisions.append(self._decision(
            "loop_detection", action, not repeated,
            "Call sequence is progressing." if not repeated else "Identical consecutive tool calls indicate a loop.",
        ))

        within_limit = len(self.history) < self.max_tool_calls
        decisions.append(self._decision(
            "tool_call_limit", action, within_limit,
            f"Call {len(self.history) + 1} of {self.max_tool_calls}." if within_limit else "Per-task tool-call limit exceeded.",
        ))

        sensitive = action in {"restart_service", "scale_service"}
        decisions.append(self._decision(
            "human_approval", action, "allow" if not sensitive else "approval_required",
            "Action is safe to run automatically." if not sensitive else "Sensitive operational action requires explicit approval.",
        ))
        self.history.append(action)
        return decisions

    def mark_complete(self) -> PolicyDecision:
        self.task_complete = True
        return self._decision("task_completion", "task", True, "Task marked complete; further actions are denied.")

    def deny_after_completion(self, call: ToolCall) -> PolicyDecision:
        return self._decision("stop_after_completion", call.name, False, "Task is complete; no further tool calls are permitted.")

    def _validate_schema(self, action: str, arguments: dict[str, Any]) -> tuple[bool, str]:
        schema = self.registered_tools[action]
        required = schema.get("required", [])
        missing = [key for key in required if key not in arguments]
        if missing:
            return False, f"Missing required argument(s): {', '.join(missing)}."
        allowed = set(schema.get("properties", []))
        unknown = set(arguments) - allowed
        if unknown:
            return False, f"Unknown argument(s): {', '.join(sorted(unknown))}."
        return True, "Arguments match the strict tool schema."

    @staticmethod
    def _decision(policy_name: str, action: str, allowed: bool | str, reason: str) -> PolicyDecision:
        decision = allowed if isinstance(allowed, str) else ("allow" if allowed else "deny")
        return PolicyDecision(
            policy_name=policy_name,
            action=action,
            decision=decision,
            reason=reason,
            timestamp=datetime.now(timezone.utc),
        )

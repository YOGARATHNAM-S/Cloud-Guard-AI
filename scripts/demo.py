"""Small terminal demo for the two most important safety paths."""

from backend.app.models import ToolCall
from backend.app.policy import PolicyEngine
from backend.app.tools import REGISTERED_TOOLS


def main() -> None:
    policy = PolicyEngine(registered_tools=REGISTERED_TOOLS)
    safe = policy.evaluate(ToolCall(name="inspect_cloudwatch_logs", arguments={"service": "payments-api"}))
    blocked = policy.evaluate(ToolCall(name="delete_all_resources", arguments={}))
    print("Successful repair evidence collection:", [item.decision for item in safe])
    print("Blocked destructive action:", [(item.policy_name, item.decision) for item in blocked])


if __name__ == "__main__":
    main()

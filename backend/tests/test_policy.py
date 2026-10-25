from app.models import ToolCall
from app.policy import PolicyEngine
from app.tools import REGISTERED_TOOLS


def engine():
    return PolicyEngine(registered_tools=REGISTERED_TOOLS)


def test_destructive_action_is_denied():
    decisions = engine().evaluate(ToolCall(name="delete_all_resources", arguments={}))
    assert decisions[0].decision == "deny"


def test_unregistered_tool_is_denied():
    decisions = engine().evaluate(ToolCall(name="shell", arguments={}))
    assert decisions[0].policy_name == "registered_tool"
    assert decisions[0].decision == "deny"


def test_loop_is_denied():
    policy = engine()
    policy.evaluate(ToolCall(name="inspect_cloudwatch_logs", arguments={"service": "x"}))
    decisions = policy.evaluate(ToolCall(name="inspect_cloudwatch_logs", arguments={"service": "x"}))
    assert any(d.policy_name == "loop_detection" and d.decision == "deny" for d in decisions)


def test_sensitive_action_requires_approval():
    decisions = engine().evaluate(ToolCall(name="restart_service", arguments={"service": "x"}))
    assert any(d.policy_name == "human_approval" and d.decision == "approval_required" for d in decisions)


def test_secrets_are_denied():
    decisions = engine().evaluate(ToolCall(name="inspect_cloudwatch_logs", arguments={"service": ".env"}))
    assert any(d.policy_name == "authorized_arguments" and d.decision == "deny" for d in decisions)


def test_schema_is_strict():
    decisions = engine().evaluate(ToolCall(name="inspect_cloudwatch_logs", arguments={"service": "x", "extra": 1}))
    assert any(d.policy_name == "strict_argument_schema" and d.decision == "deny" for d in decisions)

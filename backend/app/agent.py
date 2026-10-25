from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .models import Diagnosis, Evidence, IncidentRequest, ToolCall, WorkflowResponse
from .policy import PolicyEngine
from .tools import REGISTERED_TOOLS, TOOL_HANDLERS


@dataclass
class InvestigationAgent:
    def investigate(self, request: IncidentRequest) -> WorkflowResponse:
        engine = PolicyEngine(registered_tools=REGISTERED_TOOLS)
        incident = request.description
        inspection = ToolCall(name="inspect_cloudwatch_logs", arguments={"service": "payments-api"})
        inspection_decisions = engine.evaluate(inspection)
        inspection_allowed = all(d.decision == "allow" for d in inspection_decisions)
        if not inspection_allowed:
            raise RuntimeError("Policy blocked the required evidence collection step.")
        logs = TOOL_HANDLERS[inspection.name](**inspection.arguments)

        diagnosis = Diagnosis(
            root_cause="orders-db connection pool exhaustion is cascading into payments-api retries.",
            confidence=0.94,
            evidence=[
                Evidence(source="simulated CloudWatch fixture", detail="orders-db has 100/100 active connections."),
                Evidence(source="simulated CloudWatch fixture", detail="payments-api reports pool exhaustion and elevated latency."),
            ],
            assumptions=["This MVP uses simulated logs only.", "Restarting the service is reversible in the mock environment."],
            remediation_plan=["Preview a payments-api restart.", "Require approval for the sensitive restart.", "Verify service health after execution."],
        )
        proposed = [ToolCall(name="restart_service", arguments={"service": "payments-api"})]
        decisions = inspection_decisions
        for call in proposed:
            decisions.extend(engine.evaluate(call))
        decisions.append(engine.mark_complete())
        return WorkflowResponse(
            workflow_id=str(uuid4()),
            incident=incident,
            diagnosis=diagnosis,
            proposed_actions=proposed,
            policy_decisions=decisions,
            approval_required=True,
            status="approval_required",
        )


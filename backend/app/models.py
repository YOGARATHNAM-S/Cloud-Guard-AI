from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


Decision = Literal["allow", "deny", "approval_required"]


class IncidentRequest(BaseModel):
    description: str = Field(min_length=5, max_length=2000)


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class PolicyDecision(BaseModel):
    policy_name: str
    action: str
    decision: Decision
    reason: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Evidence(BaseModel):
    source: str
    detail: str


class Diagnosis(BaseModel):
    root_cause: str
    confidence: float = Field(ge=0, le=1)
    evidence: list[Evidence]
    assumptions: list[str]
    remediation_plan: list[str]


class WorkflowResponse(BaseModel):
    workflow_id: str
    incident: str
    diagnosis: Diagnosis
    proposed_actions: list[ToolCall]
    policy_decisions: list[PolicyDecision]
    approval_required: bool
    status: str
    data_mode: Literal["mock"] = "mock"


import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agent import InvestigationAgent
from .evaluation import SCENARIOS, run_evaluation
from .models import IncidentRequest
from .storage import initialize, recent_events, record_decisions
from .tools import SAMPLE_LOGS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize()
    logging.info("CloudGuard AI started in mock mode; real cloud execution is disabled.")
    yield


app = FastAPI(title="CloudGuard AI API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "data_mode": "mock", "failproofai": {"available": False, "active": False, "reason": "Optional integration not configured."}}


@app.get("/api/dashboard")
def dashboard():
    return {"data_mode": "mock", "kpis": {"total_tasks": 128, "successful_runs": 117, "failed_runs": 7, "blocked_actions": 23, "success_rate": 91.4},
            "active_sessions": 3, "recent_events": [{"time": "2m ago", "event": "Destructive action blocked", "severity": "high"},
            {"time": "8m ago", "event": "Incident diagnosis completed", "severity": "info"}],
            "timeline": [{"time": "17:42:08", "label": "Evidence collected", "status": "allowed"},
                         {"time": "17:42:09", "label": "Restart proposed", "status": "approval_required"}]}


@app.post("/api/investigate")
def investigate(request: IncidentRequest):
    try:
        result = InvestigationAgent().investigate(request)
        record_decisions(result.policy_decisions)
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/api/logs")
def logs():
    return {"data_mode": "mock", "logs": SAMPLE_LOGS}


@app.get("/api/audit")
def audit():
    initialize()
    return {"events": recent_events()}


@app.get("/api/policies")
def policies():
    return {"policies": [{"name": "deny_destructive_actions", "enabled": True}, {"name": "loop_detection", "enabled": True},
                         {"name": "human_approval", "enabled": True}, {"name": "strict_argument_schema", "enabled": True}]}


@app.get("/api/evaluation")
def evaluation():
    return run_evaluation()


@app.get("/api/scenarios")
def scenarios():
    return [{"name": name, "description": description} for name, description in SCENARIOS]

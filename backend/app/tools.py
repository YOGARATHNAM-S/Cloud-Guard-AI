from typing import Any


SAMPLE_LOGS = [
    {"timestamp": "2026-10-25T17:30:01Z", "service": "payments-api", "level": "ERROR",
     "message": "Connection pool exhausted while contacting orders-db"},
    {"timestamp": "2026-10-25T17:30:02Z", "service": "payments-api", "level": "WARN",
     "message": "Retry budget at 90%; request latency above 2s"},
    {"timestamp": "2026-10-25T17:30:03Z", "service": "orders-db", "level": "INFO",
     "message": "Active connections: 100/100"},
]


def inspect_cloudwatch_logs(service: str) -> dict[str, Any]:
    return {"service": service, "logs": SAMPLE_LOGS, "source": "simulated CloudWatch fixture"}


def restart_service(service: str) -> dict[str, Any]:
    return {"service": service, "status": "restarted", "source": "mock execution"}


def verify_health(service: str) -> dict[str, Any]:
    return {"service": service, "healthy": True, "latency_ms": 120, "source": "simulated health check"}


REGISTERED_TOOLS = {
    "inspect_cloudwatch_logs": {"required": ["service"], "properties": ["service"]},
    "restart_service": {"required": ["service"], "properties": ["service"]},
    "verify_health": {"required": ["service"], "properties": ["service"]},
}

TOOL_HANDLERS = {
    "inspect_cloudwatch_logs": inspect_cloudwatch_logs,
    "restart_service": restart_service,
    "verify_health": verify_health,
}


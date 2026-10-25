import json
import os
import sqlite3
from pathlib import Path

from .models import PolicyDecision


DB_PATH = Path(os.getenv("CLOUDGUARD_DB_PATH", "cloudguard.db"))


def initialize() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_name TEXT NOT NULL,
                action TEXT NOT NULL,
                decision TEXT NOT NULL,
                reason TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                details TEXT
            )"""
        )
        connection.commit()


def record_decisions(decisions: list[PolicyDecision]) -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.executemany(
            "INSERT INTO audit_events(policy_name, action, decision, reason, timestamp, details) VALUES (?, ?, ?, ?, ?, ?)",
            [(item.policy_name, item.action, item.decision, item.reason, item.timestamp.isoformat(), json.dumps({}))
             for item in decisions],
        )
        connection.commit()


def recent_events(limit: int = 50) -> list[dict[str, str]]:
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT policy_name, action, decision, reason, timestamp FROM audit_events ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


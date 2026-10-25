# CloudGuard AI

CloudGuard AI is a fail-safe cloud operations assistant that investigates incidents, proposes safe remediation, and evaluates every tool call with deterministic policies before execution.

## Run locally

### API

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

Run tests with `pytest backend\tests`.

Run the safety demo with `python -m scripts.demo`.

### Dashboard

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. The Next.js development proxy forwards `/api` requests to `http://localhost:8000`, avoiding local CORS issues. Set `NEXT_PUBLIC_API_URL` when the API is hosted elsewhere.

## Demo flow

1. Enter an incident and select **Investigate incident**.
2. Review the simulated evidence and diagnosis.
3. Observe that the proposed restart is marked `approval_required`; no handler is executed by the investigation endpoint.
4. Select **Run evaluation** to execute each failure scenario three times. Results are measured mock runs, not fabricated production telemetry.

## Safety and limitations

The registered tool allow-list, strict argument schemas, destructive-action block, secret/path block, loop detection, per-task call limit, completion guard, and approval gate are local deterministic controls. No arbitrary shell, real AWS, or destructive operation is available.

FailproofAI is intentionally not claimed as active. The API health endpoint reports the optional integration as unavailable unless a supported official CLI/hooks setup is configured. The deterministic controls remain active regardless. Before enabling an integration, verify the installed CLI and use its current official documentation; no undocumented API or configuration field is assumed here.

Estimated cost is omitted when provider usage data is unavailable. Sample dashboard values are clearly labeled mock data.

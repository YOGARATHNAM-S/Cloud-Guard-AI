"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "";
type Dashboard = { kpis: Record<string, number>; active_sessions: number; recent_events: { time: string; event: string; severity: string }[]; timeline: { time: string; label: string; status: string }[] };
type Workflow = { diagnosis: { root_cause: string; confidence: number; evidence: { source: string; detail: string }[]; remediation_plan: string[] }; status: string; approval_required: boolean; policy_decisions: { policy_name: string; decision: string; reason: string }[] };

export default function Home() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [incident, setIncident] = useState("Payments API is timing out and returning 5xx errors");
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [evaluation, setEvaluation] = useState<{ all_runs_pass_rate: number; policy_violation_count: number; scenarios: { scenario: string; pass_rate: number }[] } | null>(null);
  const [loading, setLoading] = useState(false);
  const [connectionError, setConnectionError] = useState("");
  async function apiFetch(path: string, options?: RequestInit) {
    const response = await fetch(`${API}/api/${path}`, options);
    if (!response.ok) throw new Error(`API returned ${response.status}`);
    return response.json();
  }
  useEffect(() => {
    apiFetch("dashboard").then(setDashboard).catch(() => setConnectionError("The API is unavailable. Start it with: uvicorn backend.app.main:app --reload --port 8000"));
  }, []);
  async function investigate() {
    setLoading(true);
    setConnectionError("");
    try { setWorkflow(await apiFetch("investigate", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ description: incident }) })); }
    catch { setConnectionError("Investigation could not reach the API. Confirm the backend is running on port 8000."); }
    finally { setLoading(false); }
  }
  async function runEvaluation() {
    setConnectionError("");
    try { setEvaluation(await apiFetch("evaluation")); }
    catch { setConnectionError("Evaluation could not reach the API. Confirm the backend is running on port 8000."); }
  }
  const kpis = dashboard?.kpis || {};
  return <main className="min-h-screen">
    <header className="border-b border-slate-800 px-6 py-5"><div className="mx-auto flex max-w-7xl items-center justify-between">
      <div><div className="flex items-center gap-3"><span className="h-3 w-3 rounded-full bg-cyan-400 shadow-[0_0_18px_#22d3ee]" /><h1 className="text-xl font-semibold tracking-tight">CloudGuard <span className="text-cyan-300">AI</span></h1></div><p className="mt-1 text-xs text-slate-400">Autonomous operations, bounded by deterministic safety</p></div>
      <span className="rounded-full border border-amber-400/30 bg-amber-400/10 px-3 py-1 text-xs text-amber-300">MOCK MODE · REAL CLOUD DISABLED</span>
    </div></header>
    <div className="mx-auto grid max-w-7xl gap-6 px-6 py-8 lg:grid-cols-[1fr_360px]">
      {connectionError && <div className="fixed right-6 top-6 z-10 max-w-md rounded-lg border border-red-400/30 bg-red-950/90 px-4 py-3 text-sm text-red-200 shadow-xl">{connectionError}</div>}
      <section className="space-y-6">
        <div className="grid grid-cols-2 gap-3 md:grid-cols-5">{[["Total tasks", kpis.total_tasks], ["Success rate", `${kpis.success_rate || 0}%`], ["Failed runs", kpis.failed_runs], ["Blocked", kpis.blocked_actions], ["Sessions", dashboard?.active_sessions || 0]].map(([label, value]) => <div className="glass rounded-xl p-4" key={String(label)}><p className="text-xs text-slate-400">{label}</p><p className="mt-2 text-2xl font-semibold">{value}</p></div>)}</div>
        <div className="glass rounded-2xl p-6"><div className="mb-5 flex items-center justify-between"><div><h2 className="text-lg font-semibold">Incident investigation</h2><p className="text-sm text-slate-400">Evidence-first diagnosis with approval-gated remediation</p></div><span className="rounded bg-violet-400/10 px-2 py-1 text-xs text-violet-300">SIMULATED TELEMETRY</span></div>
          <textarea value={incident} onChange={e => setIncident(e.target.value)} className="h-24 w-full rounded-lg border border-slate-700 bg-slate-950/50 p-3 text-sm outline-none ring-cyan-400 focus:ring-1" />
          <button onClick={investigate} disabled={loading} className="mt-3 rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 disabled:opacity-50">{loading ? "Investigating..." : "Investigate incident"}</button>
          {workflow && <div className="mt-6 space-y-4 border-t border-slate-800 pt-5"><div className="flex items-center justify-between"><h3 className="font-medium">Diagnosis</h3><span className="rounded-full bg-amber-400/10 px-3 py-1 text-xs text-amber-300">{workflow.status.replace("_", " ")}</span></div><p className="text-sm text-slate-300">{workflow.diagnosis.root_cause}</p><p className="text-xs text-cyan-300">Confidence {(workflow.diagnosis.confidence * 100).toFixed(0)}% · Approval required before restart</p><div className="grid gap-2 md:grid-cols-2">{workflow.diagnosis.evidence.map(e => <div className="rounded-lg bg-slate-950/40 p-3 text-xs" key={e.detail}><p className="text-slate-500">{e.source}</p><p className="mt-1 text-slate-300">{e.detail}</p></div>)}</div><div><p className="mb-2 text-xs font-medium uppercase tracking-wider text-slate-500">Policy decisions</p>{workflow.policy_decisions.slice(-7).map(d => <div className="flex justify-between border-b border-slate-800 py-2 text-xs" key={`${d.policy_name}-${d.reason}`}><span>{d.policy_name}</span><span className={d.decision === "allow" ? "text-emerald-300" : "text-amber-300"}>{d.decision}</span></div>)}</div></div>}
        </div>
        <div className="glass rounded-2xl p-6"><div className="flex items-center justify-between"><div><h2 className="text-lg font-semibold">Failure simulation lab</h2><p className="text-sm text-slate-400">Three measured mock runs per scenario</p></div><button onClick={runEvaluation} className="rounded-lg border border-violet-400/40 px-3 py-2 text-xs text-violet-200">Run evaluation</button></div>{evaluation && <><div className="mt-5 grid grid-cols-2 gap-3"><div className="rounded-lg bg-slate-950/40 p-3"><p className="text-xs text-slate-500">All-runs pass rate</p><p className="mt-1 text-xl text-emerald-300">{(evaluation.all_runs_pass_rate * 100).toFixed(0)}%</p></div><div className="rounded-lg bg-slate-950/40 p-3"><p className="text-xs text-slate-500">Policy violations</p><p className="mt-1 text-xl">{evaluation.policy_violation_count}</p></div></div><div className="mt-4 space-y-2">{evaluation.scenarios.map(s => <div className="flex justify-between rounded bg-slate-950/30 px-3 py-2 text-sm" key={s.scenario}><span>{s.scenario.replaceAll("_", " ")}</span><span className="text-emerald-300">{(s.pass_rate * 100).toFixed(0)}% pass</span></div>)}</div></>}</div>
      </section>
      <aside className="space-y-6"><div className="glass rounded-2xl p-5"><h2 className="font-semibold">Execution timeline</h2><div className="mt-4 space-y-4">{(dashboard?.timeline || []).map(item => <div className="flex gap-3 text-sm" key={item.time}><span className="mt-1 h-2 w-2 rounded-full bg-cyan-300" /><div><p>{item.label}</p><p className="text-xs text-slate-500">{item.time} · {item.status}</p></div></div>)}</div></div><div className="glass rounded-2xl p-5"><h2 className="font-semibold">Recent security events</h2><div className="mt-4 space-y-3">{(dashboard?.recent_events || []).map(event => <div className="border-b border-slate-800 pb-3 text-sm" key={event.event}><div className="flex justify-between"><span>{event.event}</span><span className="text-xs text-amber-300">{event.severity}</span></div><p className="mt-1 text-xs text-slate-500">{event.time}</p></div>)}</div></div><div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/5 p-5"><p className="text-xs uppercase tracking-wider text-cyan-300">Safety guarantee</p><p className="mt-2 text-sm leading-6 text-slate-300">Every tool call is evaluated before execution. The model is never the security boundary.</p></div></aside>
    </div>
  </main>;
}

"""Benchmark for breach_report.py. Run: python eval.py   -> prints PASS/FAIL per check and a score."""
from pathlib import Path
import pandas as pd
import breach_report as br

D = Path("data")
df, dropped = br.load(D)
raw = pd.read_csv(D / "tickets.csv", parse_dates=["created_at", "first_response_at"])
R = []
def check(name, ok, info=""): R.append(ok); print(("PASS" if ok else "FAIL"), name, info)

# 1 integrity of cleaning
check("no duplicate ticket_id", not df.ticket_id.duplicated().any())
check("de-dup keeps helpdesk row", (df[df.ticket_id.isin(raw[raw.ticket_id.duplicated()].ticket_id)].source_system == "helpdesk").all())
check("roster join: no dropped tickets", dropped == 0, f"dropped={dropped}")
check("roster join: one row per ticket", len(df) == raw.ticket_id.nunique())

# 2 timezone: voice callbacks are only taken 08-22 IST, so a correct conversion puts all voice inside it
v = df[df.channel == "voice"]
inside = lambda ts: ((ts.dt.hour >= 8) & (ts.dt.hour < 22)).mean()
check("UTC->IST conversion consistent with IVR hours", inside(v.created_ist) == 1.0 and inside(v.created_at) < 1.0,
      f"IST={inside(v.created_ist):.3f} rawUTC={inside(v.created_at):.3f}")

# 3 roster date-awareness: agents who moved 30 Jun 2025 get the right shift either side
mv = df[df.agent_id.isin(["A3002", "A3003"])]
pre, post = mv[mv.created_ist < "2025-06-30"], mv[mv.created_ist >= "2025-06-30"]
check("moved agents: Night before, Day after", (pre.agent_shift == "Night").all() and (post.agent_shift == "Day").all(),
      f"pre={pre.agent_shift.unique()} post={post.agent_shift.unique()}")

# 4 sensitivity: wrong pipelines must change the answer (otherwise the checks above prove nothing)
naive = raw.assign(frt=(raw.first_response_at - raw.created_at).dt.total_seconds() / 60)
naive_b = (naive.frt > naive.channel.map(br.TARGET_MIN)).sum()
check("skipping de-dup would inflate breaches", naive_b > df.breach.sum(), f"{naive_b} vs {df.breach.sum()}")

# 5 fairness: does the agent-level number depend on which shift the agent sits in? (confound = bad metric)
df["inherited"] = df.arrival_shift != df.agent_shift
a = df.groupby(["agent_id", "agent_shift"]).apply(
    lambda g: pd.Series({"raw": g.breach.mean(), "own": g[~g.inherited].breach.mean() if (~g.inherited).any() else float("nan")}),
    include_groups=False).reset_index()
gap = lambda c: a.groupby("agent_shift")[c].mean().pipe(lambda s: s.max() - s.min())
print(f"INFO shift gap in mean agent breach rate: raw={gap('raw'):.3f} own-shift-only={gap('own'):.3f}")
check("agent metric not confounded by shift (gap < 0.05)", gap("own") < 0.05)
check("report exposes an own-shift (controllable) rate", "own_rate" in br.summarise(df, ["agent_id"]).columns)

print(f"SCORE {sum(R)}/{len(R)}")

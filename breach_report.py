"""Weekly first-response SLA breach report for Vireo Audio.

Usage: python breach_report.py [data_dir] [out_dir]
Writes out/breaches_by_agent_week.csv, out/breaches_by_shift_week.csv, out/report.md
"""
import sys
from pathlib import Path

import pandas as pd

TARGET_MIN = {"chat": 15, "voice": 120, "social": 240, "email": 480}  # policy s3
CREDIT_INR = 350  # policy s3
IST = pd.Timedelta(minutes=330)  # export is UTC, shifts are IST


def shift_of(ts_ist):
    h = ts_ist.dt.hour
    return pd.Series(
        ["Morning" if 6 <= x < 14 else "Day" if 14 <= x < 22 else "Night" for x in h],
        index=ts_ist.index,
    )


def load(data):
    t = pd.read_csv(data / "tickets.csv", parse_dates=["created_at", "first_response_at"])
    # migration re-import: same ticket_id under both systems, identical except csat 0 vs blank
    t = t.sort_values("source_system").drop_duplicates("ticket_id", keep="first")  # helpdesk < legacy_fd
    t["created_ist"] = t.created_at + IST
    t["frt_min"] = (t.first_response_at - t.created_at).dt.total_seconds() / 60
    t["breach"] = t.frt_min > t.channel.map(TARGET_MIN)
    t["arrival_shift"] = shift_of(t.created_ist)
    t["week"] = t.created_ist.dt.to_period("W-SUN").dt.start_time.dt.date

    a = pd.read_csv(data / "agents.csv", parse_dates=["from_date", "to_date"])
    a["to_date"] = a.to_date.fillna(pd.Timestamp("2100-01-01"))
    # date-aware roster join: the assignment that was live when the ticket was created
    m = t.merge(a[["agent_id", "name", "site", "shift", "from_date", "to_date"]], on="agent_id", how="left")
    d = m.created_ist.dt.normalize()
    m = m[(d >= m.from_date) & (d <= m.to_date)]
    m = m.rename(columns={"shift": "agent_shift"})
    # ponytail: tickets with no live roster row for their agent are dropped; count them below
    return m, len(t) - len(m)


def summarise(df, keys):
    g = df.groupby(keys)
    out = g.agg(tickets=("breach", "size"), breaches=("breach", "sum"),
                inherited=("inherited", "sum")).reset_index()
    out["breach_rate"] = (out.breaches / out.tickets).round(3)
    own = df[~df.inherited].groupby(keys).breach.mean().rename("own_rate").round(3)  # tickets that arrived on the agent's own shift
    out = out.merge(own.reset_index(), on=keys, how="left")
    out["credit_inr"] = out.breaches * CREDIT_INR
    return out


def main(data, out):
    df, dropped = load(Path(data))
    out = Path(out); out.mkdir(exist_ok=True)
    # inherited: ticket arrived on another shift's watch than the shift of the agent who resolved it
    df["inherited"] = df.arrival_shift != df.agent_shift
    summarise(df, ["week", "agent_id", "name", "agent_shift"]).to_csv(out / "breaches_by_agent_week.csv", index=False)
    by_arrival = summarise(df, ["week", "arrival_shift"])
    by_arrival.to_csv(out / "breaches_by_shift_week.csv", index=False)

    lines = ["# Breach report", f"Tickets: {len(df)} after de-dup; {dropped} dropped (no live roster row).", ""]
    for name, key in [("Shift the ticket ARRIVED in (IST)", "arrival_shift"),
                      ("Shift of the agent who RESOLVED it", "agent_shift")]:
        s = summarise(df, [key]).sort_values("breaches", ascending=False)
        lines += [f"## {name}", s.to_markdown(index=False), ""]
    x = df[df.breach].groupby(["agent_shift", "arrival_shift"]).size().unstack(fill_value=0)
    lines += ["## Breaches: resolver shift (rows) vs arrival shift (cols)", x.to_markdown(), ""]
    ag = summarise(df[df.created_ist >= df.created_ist.max() - pd.Timedelta(days=28)],
                   ["agent_id", "name", "agent_shift"]).sort_values("breaches", ascending=False)
    lines += ["## Agents, last 4 weeks", ag.head(15).to_markdown(index=False)]
    (out / "report.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main(*(sys.argv[1:3] or ["data", "out"]))

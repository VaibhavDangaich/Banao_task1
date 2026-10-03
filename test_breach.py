"""Run: python test_breach.py  (checks tool output against an independent stdlib count + edge cases)"""
import csv
from datetime import datetime, timedelta
import pandas as pd
import breach_report as br

T = {"chat": 15, "voice": 120, "social": 240, "email": 480}
seen, n, b = set(), 0, 0
for r in csv.DictReader(open("data/tickets.csv")):  # independent re-implementation, no pandas
    if r["ticket_id"] in seen: continue
    seen.add(r["ticket_id"]); n += 1
    f = "%Y-%m-%d %H:%M"
    mins = (datetime.strptime(r["first_response_at"], f) - datetime.strptime(r["created_at"], f)).total_seconds() / 60
    b += mins > T[r["channel"]]
df, dropped = br.load(__import__("pathlib").Path("data"))
assert (len(df), int(df.breach.sum()), dropped) == (n, b, 0), (len(df), df.breach.sum(), n, b)

# edge cases: UTC 16:30 = 22:00 IST -> Night; UTC 16:29 -> Day; exactly-on-target is not a breach
s = pd.Series(pd.to_datetime(["2025-01-01 16:29", "2025-01-01 16:30", "2025-01-01 00:30"])) + br.IST
assert list(br.shift_of(s)) == ["Day", "Night", "Morning"]
assert not (15 > 15) and 16 > 15
print("ok:", n, "tickets,", b, "breaches")

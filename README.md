# Vireo first-response breach report

    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/python breach_report.py data out     # data/ holds the 8 pack files
    .venv/bin/python test_breach.py                # cross-check vs independent stdlib count
    .venv/bin/python eval.py                       # 12 checks, prints SCORE 12/12

Outputs in `out/`: `report.md`, `breaches_by_agent_week.csv`, `breaches_by_shift_week.csv`.

Decisions: de-dup on ticket_id (keep helpdesk row); timestamps UTC -> IST (+5:30) before assigning a shift;
breach = first response later than policy s3 target; roster joined by agent_id and date; every table is cut
two ways: shift the ticket **arrived** in vs shift of the agent who **resolved** it.
Sample output: `sample/report.md`.
No LLM/paid calls at runtime; AI was used to build it (see submission-form.md).

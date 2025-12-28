"""Alarm och event timeline.

Förväntar sig en tabell "text_logs" med kolumner:
- ts
- level
- message
"""

import pandas as pd

logs = load("text_logs")

alarms = logs[logs["level"].str.upper().isin(["ALARM", "ERROR", "WARN"])].copy()
alarms = alarms.sort_values("ts")
alarms["event_type"] = "alarm"

save_table("alarm_timeline", alarms)
log(f"Saved {len(alarms)} alarm events")

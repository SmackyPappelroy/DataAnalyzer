"""DB-join och tidsynk mellan SQL Server-data och CSV.

Förväntar sig tabeller:
- sql_series (ts, value)
- csv_series (ts, value)
"""

import pandas as pd

sql_series = load("sql_series").sort_values("ts")
csv_series = load("csv_series").sort_values("ts")

merged = pd.merge_asof(
    sql_series,
    csv_series,
    on="ts",
    direction="nearest",
    tolerance=pd.Timedelta("1s"),
    suffixes=("_sql", "_csv"),
)

save_table("joined_time_sync", merged)
log("Joined SQL Server and CSV series with nearest timestamp")

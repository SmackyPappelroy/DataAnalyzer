"""Trend och avvikelse för analog signal.

Förväntar sig en tabell "analog_signal" med kolumner:
- ts
- value
"""

import pandas as pd

window = int(params.get("window", 60))
threshold = float(params.get("threshold", 3.0))

signal = load("analog_signal").sort_values("ts")
signal["rolling_mean"] = signal["value"].rolling(window=window, min_periods=1).mean()
signal["rolling_std"] = signal["value"].rolling(window=window, min_periods=1).std().fillna(0)

signal["zscore"] = (signal["value"] - signal["rolling_mean"]) / signal["rolling_std"].replace(0, 1)
signal["is_outlier"] = signal["zscore"].abs() > threshold

save_table("analog_trend_outliers", signal)
log("Computed rolling stats and outliers")

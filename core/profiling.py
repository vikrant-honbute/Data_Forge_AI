from __future__ import annotations

from typing import Any, Dict

import pandas as pd
from pandas.api.types import infer_dtype, is_numeric_dtype


def _safe_float(value: Any) -> float | None:
	if pd.isna(value):
		return None
	return float(value)


def build_profile(df: pd.DataFrame) -> Dict[str, Any]:
	if df is None:
		raise ValueError("df must be a pandas DataFrame, got None")

	rows = int(df.shape[0])
	cols = int(df.shape[1])
	duplicate_rows = int(df.duplicated().sum()) if rows else 0

	column_stats: Dict[str, Dict[str, Any]] = {}
	for column in df.columns:
		series = df[column]
		non_null = series.dropna()

		if non_null.empty:
			dtype_inferred = "empty"
		else:
			dtype_inferred = infer_dtype(non_null, skipna=True)

		missing_count = int(series.isna().sum())
		missing_pct = (missing_count / rows) * 100 if rows else 0.0
		unique_count = int(non_null.nunique()) if rows else 0
		sample_values = non_null.head(5).tolist()

		stats: Dict[str, Any] = {
			"dtype_inferred": dtype_inferred,
			"missing_count": missing_count,
			"missing_pct": missing_pct,
			"unique_count": unique_count,
			"sample_values": sample_values,
		}

		if is_numeric_dtype(series):
			numeric = pd.to_numeric(series, errors="coerce")
			numeric_non_null = numeric.dropna()
			if numeric_non_null.empty:
				numeric_stats = {
					"mean": None,
					"median": None,
					"std": None,
					"min": None,
					"max": None,
					"skew": None,
				}
			else:
				numeric_stats = {
					"mean": _safe_float(numeric_non_null.mean()),
					"median": _safe_float(numeric_non_null.median()),
					"std": _safe_float(numeric_non_null.std()),
					"min": _safe_float(numeric_non_null.min()),
					"max": _safe_float(numeric_non_null.max()),
					"skew": _safe_float(numeric_non_null.skew()),
				}

			stats["numeric"] = numeric_stats

		column_stats[str(column)] = stats

	return {
		"dataset": {
			"n_rows": rows,
			"n_cols": cols,
			"duplicate_rows": duplicate_rows,
		},
		"columns": column_stats,
	}

from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd


def generate_suggestions(df: pd.DataFrame) -> List[Dict[str, Any]]:
	if df is None:
		raise ValueError("df must be provided for suggestion generation")

	suggestions: List[Dict[str, Any]] = []

	n_rows = int(len(df))
	duplicate_rows = int(df.duplicated().sum()) if n_rows else 0
	if duplicate_rows > 0:
		suggestions.append(
			{
				"id": "duplicate_rows",
				"type": "duplicate_rows",
				"column": None,
				"issue": f"{duplicate_rows} duplicate rows",
				"action": "remove_duplicates",
				"params": {"count": duplicate_rows},
				"confidence": 0.8,
			}
		)

	for column in df.columns:
		series = df[column]
		missing_count = int(series.isna().sum())
		missing_pct = (missing_count / n_rows) * 100 if n_rows else 0.0

		if missing_count > 0:
			suggestions.append(
				{
					"id": f"missing_{column}",
					"type": "missing_values",
					"column": str(column),
					"issue": f"{missing_pct:.0f}% missing values",
					"action": "fill_median",
					"params": {
						"missing_count": missing_count,
						"missing_pct": float(missing_pct),
					},
					"confidence": 0.85,
				}
			)

		if missing_pct > 40.0:
			suggestions.append(
				{
					"id": f"high_missing_{column}",
					"type": "high_missing_pct",
					"column": str(column),
					"issue": f"{missing_pct:.0f}% missing values",
					"action": "drop_column",
					"params": {"missing_pct": float(missing_pct)},
					"confidence": 0.7,
				}
			)

		if pd.api.types.is_numeric_dtype(series):
			numeric = pd.to_numeric(series, errors="coerce").dropna()
			if not numeric.empty:
				q1 = float(numeric.quantile(0.25))
				q3 = float(numeric.quantile(0.75))
				iqr = q3 - q1
				lower = q1 - 1.5 * iqr
				upper = q3 + 1.5 * iqr
				outlier_count = int(((numeric < lower) | (numeric > upper)).sum())

				if outlier_count > 0:
					suggestions.append(
						{
							"id": f"outliers_{column}",
							"type": "numeric_outliers",
							"column": str(column),
							"issue": f"{outlier_count} outliers detected (IQR)",
							"action": "remove_outliers",
							"params": {
								"outlier_count": outlier_count,
								"lower_bound": float(lower),
								"upper_bound": float(upper),
							},
							"confidence": 0.75,
						}
					)

	return suggestions

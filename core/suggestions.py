from __future__ import annotations

from typing import Any


def generate_suggestions(profile: dict) -> list[str]:
	suggestions: list[str] = []

	dataset = profile.get("dataset", {})
	n_rows = int(dataset.get("n_rows", 0) or 0)
	duplicate_rows = int(dataset.get("duplicate_rows", 0) or 0)

	if duplicate_rows > 0:
		suggestions.append(
			f"Dataset has {duplicate_rows} duplicate rows; consider deduplication."
		)

	columns: dict[str, Any] = profile.get("columns", {})
	for name, stats in columns.items():
		missing_count = int(stats.get("missing_count", 0) or 0)
		if missing_count > 0:
			suggestions.append(
				f"Column '{name}' has {missing_count} missing values; consider imputation."
			)

		unique_count = int(stats.get("unique_count", 0) or 0)
		if n_rows > 0 and unique_count / n_rows >= 0.95:
			suggestions.append(
				f"Column '{name}' has very high cardinality; consider encoding or dropping."
			)

		numeric = stats.get("numeric")
		if isinstance(numeric, dict):
			skew_value = numeric.get("skew")
			if isinstance(skew_value, (int, float)) and (skew_value > 1 or skew_value < -1):
				suggestions.append(
					f"Column '{name}' is highly skewed (skew={skew_value:.2f}); consider transformation."
				)

	return suggestions

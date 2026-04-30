from __future__ import annotations

from typing import Any, Callable, Dict

import pandas as pd


def fill_missing_mean(df: pd.DataFrame, column: str, params: dict | None = None) -> pd.DataFrame:
	if column not in df.columns:
		return df

	mean_value = df[column].mean()
	updated = df.copy()
	updated[column] = updated[column].fillna(mean_value)
	return updated


def fill_missing_median(df: pd.DataFrame, column: str, params: dict | None = None) -> pd.DataFrame:
	if column not in df.columns:
		return df

	numeric_column = pd.to_numeric(df[column], errors="coerce")
	median_value = numeric_column.median()
	updated = df.copy()
	updated[column] = updated[column].fillna(median_value)
	return updated


def drop_column(df: pd.DataFrame, column: str, params: dict | None = None) -> pd.DataFrame:
	if column not in df.columns:
		return df

	return df.drop(columns=[column])


def remove_duplicates(df: pd.DataFrame, column: str | None = None, params: dict | None = None) -> pd.DataFrame:
	return df.drop_duplicates()


def remove_outliers_iqr(df: pd.DataFrame, column: str, params: dict | None = None) -> pd.DataFrame:
	if column not in df.columns:
		return df

	series = df[column]
	if not pd.api.types.is_numeric_dtype(series):
		return df

	q1 = series.quantile(0.25)
	q3 = series.quantile(0.75)
	iqr = q3 - q1
	lower = q1 - 1.5 * iqr
	upper = q3 + 1.5 * iqr

	mask = series.between(lower, upper) | series.isna()
	return df[mask].copy()


ACTION_MAP: Dict[str, Callable[..., pd.DataFrame]] = {
	"fill_mean": fill_missing_mean,
	"fill_median": fill_missing_median,
	"drop_column": drop_column,
	"remove_duplicates": remove_duplicates,
	"remove_outliers": remove_outliers_iqr,
}

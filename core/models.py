from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class NumericStats(BaseModel):
	mean: Optional[float] = None
	median: Optional[float] = None
	std: Optional[float] = None
	min: Optional[float] = None
	max: Optional[float] = None
	skew: Optional[float] = None


class DatasetStats(BaseModel):
	n_rows: int
	n_cols: int
	duplicate_rows: int


class ColumnStats(BaseModel):
	dtype_inferred: str
	missing_count: int
	missing_pct: float
	unique_count: int
	sample_values: List[Any]
	numeric: Optional[NumericStats] = None


class ProfileResult(BaseModel):
	dataset: DatasetStats
	columns: Dict[str, ColumnStats]


class InsightResult(BaseModel):
	summary: str
	risks: List[str]

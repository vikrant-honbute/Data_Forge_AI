from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


def save_profile(profile: dict, out_dir: str = "data/versions") -> str:
	output_dir = Path(out_dir)
	output_dir.mkdir(parents=True, exist_ok=True)

	timestamp = datetime.now().isoformat(timespec="seconds").replace(":", "")
	file_path = output_dir / f"profile_{timestamp}.json"

	with file_path.open("w", encoding="utf-8") as handle:
		json.dump(profile, handle, ensure_ascii=False, indent=2)

	return str(file_path)


def save_version(df: pd.DataFrame, version_id: str, actions_applied: list[str]) -> None:
	versions_dir = Path("data_versions")
	versions_dir.mkdir(parents=True, exist_ok=True)

	file_name = f"{version_id}.csv"
	file_path = versions_dir / file_name
	df.to_csv(file_path, index=False)

	metadata_path = versions_dir / "metadata.json"
	if metadata_path.exists():
		try:
			metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
			if not isinstance(metadata, dict):
				metadata = {}
		except json.JSONDecodeError:
			metadata = {}
	else:
		metadata = {}

	metadata[version_id] = {
		"file": file_name,
		"actions": actions_applied,
		"timestamp": datetime.now().isoformat(timespec="seconds"),
	}

	metadata_path.write_text(
		json.dumps(metadata, ensure_ascii=False, indent=2),
		encoding="utf-8",
	)


def load_version(version_id: str) -> pd.DataFrame:
	versions_dir = Path("data_versions")
	file_path = versions_dir / f"{version_id}.csv"
	if not file_path.exists():
		raise FileNotFoundError(f"Version file not found: {file_path}")

	return pd.read_csv(file_path)

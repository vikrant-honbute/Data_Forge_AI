from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def save_profile(profile: dict, out_dir: str = "data/versions") -> str:
	output_dir = Path(out_dir)
	output_dir.mkdir(parents=True, exist_ok=True)

	timestamp = datetime.now().isoformat(timespec="seconds").replace(":", "")
	file_path = output_dir / f"profile_{timestamp}.json"

	with file_path.open("w", encoding="utf-8") as handle:
		json.dump(profile, handle, ensure_ascii=False, indent=2)

	return str(file_path)

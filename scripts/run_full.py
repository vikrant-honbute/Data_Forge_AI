from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


def _add_repo_root_to_path() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))
    return repo_root


def main() -> int:
    repo_root = _add_repo_root_to_path()
    csv_path = repo_root / "data" / "sample.csv"

    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        return 1

    from core.llm_insights import generate_insights
    from core.profiling import build_profile
    from core.suggestions import generate_suggestions
    from core.versioning import save_profile

    df = pd.read_csv(csv_path)
    profile = build_profile(df)
    suggestions = generate_suggestions(profile)
    insights = generate_insights(profile)
    saved_path = save_profile(profile)

    output = {
        "profile": profile,
        "suggestions": suggestions,
        "insights": insights,
        "saved_path": saved_path,
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

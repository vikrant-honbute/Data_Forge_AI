from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from core.actions import ACTION_MAP


def apply_single_suggestion(df: pd.DataFrame, suggestion: Dict[str, Any]) -> pd.DataFrame:
    if df is None:
        raise ValueError("df must be provided")

    updated = df.copy()
    action_name = suggestion.get("action")
    column = suggestion.get("column")
    params = suggestion.get("params", {})

    action = ACTION_MAP.get(action_name)
    if not action:
        print(f"Unknown action '{action_name}' for suggestion '{suggestion.get('id')}'.")
        return updated

    print(f"Applying action '{action_name}' on column '{column}'.")
    return action(updated, column, params)


def apply_suggestions(
    df: pd.DataFrame,
    suggestions: List[Dict[str, Any]],
    decisions: Dict[str, str],
) -> pd.DataFrame:
    updated = df.copy()

    for suggestion in suggestions:
        suggestion_id = suggestion.get("id")
        decision = decisions.get(suggestion_id, "reject")
        if decision != "accept":
            continue

        action_name = suggestion.get("action")
        column = suggestion.get("column")
        params = suggestion.get("params", {})

        action = ACTION_MAP.get(action_name)
        if not action:
            print(f"Unknown action '{action_name}' for suggestion '{suggestion_id}'.")
            continue

        print(f"Applying action '{action_name}' on column '{column}'.")
        updated = action(updated, column, params)

    return updated

from __future__ import annotations

import streamlit as st
import pandas as pd
import requests

from core.llm_insights import generate_explanation
from core.versioning import save_version

st.title("Data Cleaning AI Assistant")

if "df" not in st.session_state:
    st.session_state.df = None
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "actions_applied" not in st.session_state:
    st.session_state.actions_applied = []
if "uploaded_name" not in st.session_state:
    st.session_state.uploaded_name = None
if "explanations" not in st.session_state:
    st.session_state.explanations = {}


def _apply_suggestion_via_api(df: pd.DataFrame, suggestion: dict) -> pd.DataFrame | None:
    try:
        safe_df = df.astype(object).where(pd.notnull(df), None)
        records = safe_df.to_dict(orient="records")
        response = requests.post(
            "http://127.0.0.1:8000/apply-step",
            json={"data": records, "suggestion": suggestion},
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        updated_records = payload.get("updated_data", [])
        return pd.DataFrame(updated_records)
    except Exception as exc:
        st.write(f"Failed to apply suggestion: {exc}")
        return None

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
if uploaded_file is not None:
    if st.session_state.uploaded_name != uploaded_file.name:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.session_state.suggestions = []
        st.session_state.current_step = 0
        st.session_state.actions_applied = []
        st.session_state.uploaded_name = uploaded_file.name

    st.write("Preview (first 5 rows)")
    st.dataframe(st.session_state.df.head())

if st.button("Generate suggestions"):
    if st.session_state.df is None:
        st.write("Please upload a CSV file first.")
    else:
        try:
            safe_df = st.session_state.df.astype(object).where(
                pd.notnull(st.session_state.df),
                None,
            )
            records = safe_df.to_dict(orient="records")
            response = requests.post(
                "http://127.0.0.1:8000/suggest",
                json=records,
                timeout=20,
            )
            response.raise_for_status()
            payload = response.json()
            st.session_state.suggestions = payload.get("suggestions", [])
            st.session_state.current_step = 0
            st.session_state.actions_applied = []
            st.session_state.explanations = {}
        except Exception as exc:
            st.write(f"Failed to fetch suggestions: {exc}")

suggestions = st.session_state.suggestions
if suggestions:
    current_step = st.session_state.current_step
    total_steps = len(suggestions)

    if current_step < total_steps:
        suggestion = suggestions[current_step]
        suggestion_id = suggestion.get("id") or f"step_{current_step}"
        issue = suggestion.get("issue")
        column = suggestion.get("column")
        action = suggestion.get("action")
        confidence = suggestion.get("confidence")

        st.write(f"Step {current_step + 1} of {total_steps}")
        st.write(f"Issue: {issue}")
        st.write(f"Column: {column}")
        st.write(f"Suggested action: {action}")
        st.write(f"Confidence: {confidence}")

        profile_summary = {
            "n_rows": int(len(st.session_state.df)),
            "n_cols": int(st.session_state.df.shape[1]),
            "duplicate_rows": int(st.session_state.df.duplicated().sum()),
        }
        if suggestion_id not in st.session_state.explanations:
            st.session_state.explanations[suggestion_id] = generate_explanation(
                suggestion,
                profile_summary,
            )

        explanation = st.session_state.explanations.get(suggestion_id, {})
        st.write(f"Explanation: {explanation.get('explanation')}")
        st.write(f"Impact: {explanation.get('impact')}")

        accept_clicked = st.button("Accept")
        reject_clicked = st.button("Reject")

        if accept_clicked:
            updated_df = _apply_suggestion_via_api(st.session_state.df, suggestion)
            if updated_df is not None:
                st.session_state.df = updated_df
                action_name = suggestion.get("action")
                if column:
                    st.session_state.actions_applied.append(f"{action_name}_{column}")
                else:
                    st.session_state.actions_applied.append(str(action_name))
                st.session_state.current_step += 1

        if reject_clicked:
            st.session_state.current_step += 1
    else:
        st.write("All suggestions processed.")

version_id = st.text_input("Version ID", value="v1")
if st.button("Save version"):
    if st.session_state.df is None:
        st.write("Please upload a CSV file first.")
    else:
        save_version(st.session_state.df, version_id, st.session_state.actions_applied)
        st.write(f"Saved version {version_id}.")

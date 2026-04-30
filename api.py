from __future__ import annotations

from io import BytesIO
from typing import Any, Dict, List, Optional
from uuid import uuid4

import pandas as pd
from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from core.executor import apply_single_suggestion
from core.llm_insights import generate_explanation
from core.suggestions import generate_suggestions

app = FastAPI(title="Data Cleaning API")

DATA_STORE: Dict[str, pd.DataFrame] = {}


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "API is working"}


@app.post("/test")
def test(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    return payload


def _load_df(data_id: Optional[str], data: Optional[List[Dict[str, Any]]]) -> pd.DataFrame:
    if data_id:
        df = DATA_STORE.get(data_id)
        if df is None:
            raise HTTPException(status_code=404, detail="Unknown data_id")
        return df

    if data is not None:
        return pd.DataFrame(data)

    raise HTTPException(status_code=400, detail="Provide data_id or data")


class ExplainRequest(BaseModel):
    suggestion: Dict[str, Any]
    profile_summary: Optional[Dict[str, Any]] = None


@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> Dict[str, Any]:
    try:
        content = await file.read()
        df = pd.read_csv(BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {exc}") from exc

    data_id = str(uuid4())
    DATA_STORE[data_id] = df

    return {
        "data_id": data_id,
        "columns": df.columns.tolist(),
        "n_rows": int(len(df)),
    }


@app.post("/suggest")
def suggest(records: List[Dict[str, Any]] = Body(...)) -> Dict[str, Any]:
    try:
        df = pd.DataFrame(records)
        suggestions = generate_suggestions(df)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to generate suggestions: {exc}",
        ) from exc

    return {"suggestions": suggestions}


@app.post("/apply-step")
def apply_step(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    try:
        records = payload.get("data", [])
        suggestion = payload.get("suggestion", {})
        if not isinstance(records, list):
            raise ValueError("data must be a list of records")

        df = pd.DataFrame(records)
        updated = apply_single_suggestion(df, suggestion)
        updated = updated.astype(object).where(pd.notnull(updated), None)
        updated_data = updated.to_dict(orient="records")
        return {"updated_data": updated_data}
    except Exception as exc:
        return {"error": str(exc)}


@app.post("/explain")
def explain(req: ExplainRequest) -> Dict[str, Any]:
    profile_summary = req.profile_summary or {}
    return generate_explanation(req.suggestion, profile_summary)

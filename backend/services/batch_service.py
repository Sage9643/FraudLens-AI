"""
Batch prediction service.

Reuses prediction_service.predict_fraud_probabilities (vectorized) and
risk_service.classify_risk row-by-row - no prediction or risk-classification
logic is reimplemented here. Scored results are written to disk as a CSV
immediately; only lightweight metadata is kept afterward (via
database/batch_crud.py), so process memory usage stays flat regardless of
batch size and downloads survive a server restart.

Batch predictions are never written to prediction_history - they are a
separate, ephemeral-on-disk concern by design.

Performance note (why this file looks different from a naive per-row loop):
the original implementation constructed one TransactionRequest (pydantic
validation), one single-row DataFrame, one scaler.transform() call, and one
model.predict_proba() call PER ROW. Scoring is done with one
scaler.transform() call and one model.predict_proba() call PER CHUNK (see
below), via prediction_service.predict_fraud_probabilities(). Risk
classification still calls risk_service.classify_risk() once per row
(unchanged, reused as-is) because that function is cheap.

Memory note (Sprint: Render OOM fix): the previous implementation read the
entire upload into a `bytes` object, parsed it into one full-file DataFrame,
and built a second full-file output DataFrame with 5 extra columns - several
complete in-memory copies of the file alive simultaneously. For a large CSV
(e.g. the ~285k-row / ~150MB Kaggle dataset) this comfortably exceeded
Render's 512MB limit. This version streams the upload with
`pandas.read_csv(..., chunksize=...)` and appends each scored chunk directly
to the output CSV on disk, so memory usage is bounded by one chunk (~10k
rows) at a time regardless of the total file size.
"""
from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from io import TextIOWrapper
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import UploadFile

from database import batch_crud
from database.db import get_connection
from services.model_service import ModelService
from services.prediction_service import predict_fraud_probabilities
from services.risk_service import classify_risk
from utils.config import get_settings
from utils.exceptions import InvalidTransactionError

REQUIRED_COLUMNS = [f"V{i}" for i in range(1, 29)] + ["Amount"]

OUTPUT_COLUMNS = REQUIRED_COLUMNS + [
    "prediction",
    "fraud_probability",
    "confidence",
    "risk_band",
    "recommended_action",
]

CHUNK_SIZE = 10_000


def _ensure_output_dir() -> Path:
    output_dir = get_settings().batch_output_path
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _validate_header(columns: list[str]) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in columns]
    if missing:
        raise InvalidTransactionError(f"CSV is missing required column(s): {', '.join(missing)}")


def _validate_chunk_values(chunk: pd.DataFrame, running_bad_numeric: list[int], running_bad_amount: list[int]) -> None:
    """Accumulates non-numeric / negative-Amount counts across chunks so the
    error message matches the original whole-file semantics (it doesn't stop
    at the first offending chunk)."""
    numeric_view = chunk[REQUIRED_COLUMNS].apply(pd.to_numeric, errors="coerce")
    non_numeric = numeric_view.isna()
    if non_numeric.any().any():
        running_bad_numeric[0] += int(non_numeric.any(axis=1).sum())

    negative_amounts = numeric_view["Amount"] < 0
    if negative_amounts.any():
        running_bad_amount[0] += int(negative_amounts.sum())


def score_batch(file: UploadFile, model_service: ModelService) -> dict:
    start = time.monotonic()
    settings = get_settings()
    max_rows = settings.max_batch_rows

    metadata = model_service.get_metadata()
    risk_bands = metadata["risk_bands"]
    threshold = metadata["decision_threshold"]

    batch_id = uuid.uuid4().hex
    output_dir = _ensure_output_dir()
    file_path = output_dir / f"{batch_id}.csv"

    # Wrap the UploadFile's underlying binary stream as text so pandas can
    # read it directly, without ever materializing the whole upload as a
    # `bytes` object. detach() (not close()) in `finally` disconnects this
    # wrapper from the stream without closing it, since Starlette owns the
    # UploadFile's lifecycle.
    text_stream = TextIOWrapper(file.file, encoding="utf-8")

    rows_scored = 0
    fraud_count = 0
    risk_band_counts = {band: 0 for band in risk_bands["actions"].keys()}
    running_bad_numeric = [0]
    running_bad_amount = [0]
    header_written = False

    try:
        # Cheap header/empty-file pre-check before touching any data rows,
        # so missing-column and empty-file errors take precedence exactly as
        # the original whole-file validation did.
        header_df = pd.read_csv(text_stream, nrows=0)
        _validate_header(list(header_df.columns))
        text_stream.seek(0)

        try:
            reader = pd.read_csv(text_stream, chunksize=CHUNK_SIZE)
        except Exception as exc:  # noqa: BLE001
            raise InvalidTransactionError(f"Could not parse CSV: {exc}") from exc

        for chunk in reader:
            if len(chunk) == 0:
                continue

            _validate_chunk_values(chunk, running_bad_numeric, running_bad_amount)

            # Row-limit check: deliberate early-exit rather than an exact
            # whole-file count, so an oversized file is rejected without
            # fully processing it first (which would defeat the point of
            # the limit).
            if rows_scored + len(chunk) > max_rows:
                raise InvalidTransactionError(
                    f"CSV exceeds the maximum of {max_rows} rows."
                )

            if running_bad_numeric[0] or running_bad_amount[0]:
                # Keep validating subsequent chunks to accumulate accurate
                # counts (matching original whole-file semantics), but never
                # score or write a chunk once a validation error is known.
                continue

            features_df = chunk[REQUIRED_COLUMNS]
            probabilities = predict_fraud_probabilities(features_df, model_service)

            predictions = np.where(probabilities >= threshold, "Fraudulent", "Legitimate")
            confidences = np.maximum(probabilities, 1 - probabilities)

            risk_band_values: list[str] = [None] * len(probabilities)
            recommended_actions: list[str] = [None] * len(probabilities)
            for i, probability in enumerate(probabilities):
                risk = classify_risk(float(probability), risk_bands)
                risk_band_values[i] = risk.risk_band
                recommended_actions[i] = risk.recommended_action
                risk_band_counts[risk.risk_band] += 1

            chunk = chunk.copy()
            chunk["prediction"] = predictions
            chunk["fraud_probability"] = np.round(probabilities, 6)
            chunk["confidence"] = np.round(confidences, 6)
            chunk["risk_band"] = risk_band_values
            chunk["recommended_action"] = recommended_actions

            chunk[OUTPUT_COLUMNS].to_csv(
                file_path, mode="a", header=not header_written, index=False
            )
            header_written = True

            rows_scored += len(chunk)
            fraud_count += int(np.count_nonzero(predictions == "Fraudulent"))

        # Now that the whole file has been scanned, raise with the
        # accumulated counts if any validation errors were found - matching
        # the original whole-file error semantics.
        if running_bad_numeric[0]:
            raise InvalidTransactionError(
                f"CSV contains non-numeric values in one or more required columns "
                f"(affects {running_bad_numeric[0]} row(s))."
            )
        if running_bad_amount[0]:
            raise InvalidTransactionError(
                f"CSV contains {running_bad_amount[0]} row(s) with a negative Amount value."
            )

        if rows_scored == 0:
            raise InvalidTransactionError("CSV contains no data rows.")

    except InvalidTransactionError:
        file_path.unlink(missing_ok=True)
        raise
    except pd.errors.ParserError as exc:
        file_path.unlink(missing_ok=True)
        raise InvalidTransactionError(f"Could not parse CSV: {exc}") from exc
    except Exception:
        # Any other unexpected failure must not leave a partially-written
        # output file behind.
        file_path.unlink(missing_ok=True)
        raise
    finally:
        # Disconnects the text wrapper without closing Starlette's
        # underlying upload stream.
        text_stream.detach()

    fraud_rate = round(fraud_count / rows_scored, 6) if rows_scored else 0.0
    risk_distribution = [
        {"risk_band": band, "count": count} for band, count in risk_band_counts.items()
    ]

    processing_time_ms = int((time.monotonic() - start) * 1000)
    created_at = datetime.now(timezone.utc).isoformat()

    conn = get_connection()
    try:
        batch_crud.create_batch_job(
            conn,
            batch_id=batch_id,
            created_at=created_at,
            file_path=str(file_path),
            rows_scored=rows_scored,
            fraud_count=fraud_count,
            fraud_rate=fraud_rate,
            processing_time_ms=processing_time_ms,
            risk_distribution=risk_distribution,
        )
    finally:
        conn.close()

    return {
        "batch_id": batch_id,
        "rows_scored": rows_scored,
        "fraud_count": fraud_count,
        "fraud_rate": fraud_rate,
        "processing_time_ms": processing_time_ms,
        "risk_distribution": risk_distribution,
    }


def get_batch_download(batch_id: str) -> tuple[Path, str] | None:
    """Returns (file_path, created_at) for a batch, or None if the batch_id
    is unknown or its file is missing from disk."""
    conn = get_connection()
    try:
        job = batch_crud.get_batch_job(conn, batch_id)
    finally:
        conn.close()

    if job is None:
        return None

    path = Path(job["file_path"])
    if not path.exists():
        return None

    return path, job["created_at"]

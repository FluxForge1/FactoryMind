"""
FactoryMind - Machine Intelligence Integration Contract
=======================================================
Read-only adapter over the frozen machine-intelligence CSV.
"""
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
P2_CANDIDATES = (
    DATA_DIR / "FactoryMind_P2_Final_ys.csv",
    DATA_DIR / "FactoryMind_P2_Output.csv",
    Path(__file__).resolve().parent / "FactoryMind_P2_Final_ys.csv",
    Path(__file__).resolve().parent / "FactoryMind_P2_Output.csv",
)
REQUIRED_COLUMNS = (
    "machine_id", "timestamp", "case_id", "run", "failure_probability",
    "anomaly_score", "degradation_wear_score", "machine_health_score",
    "health_status", "production_bottleneck_risk", "maintenance_priority",
    "top_risk_factors", "feature_contributions", "recommended_action",
    "VB_mm_observed", "VB_mm_estimated", "VB_source", "data_quality_flag",
)
NUMERIC_SCORE_COLUMNS = (
    "failure_probability", "anomaly_score", "degradation_wear_score",
    "machine_health_score",
)


def resolve_p2_path(path: Optional[Path] = None) -> Path:
    if path is not None:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"P2 output not found: {p}")
        return p
    for candidate in P2_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("No frozen FactoryMind P2 CSV found beside p2_integration.py.")


def load_p2(path: Optional[Path] = None) -> pd.DataFrame:
    """Load and validate the frozen P2 dataset without modifying values."""
    p = resolve_p2_path(path)
    df = pd.read_csv(p)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"P2 output missing required columns: {missing}")

    keys = df[["case_id", "run"]].apply(pd.to_numeric, errors="coerce")
    if keys.isna().any().any():
        raise ValueError("P2 Case/Run contains missing or non-numeric keys.")
    if keys.duplicated().any():
        dupes = keys[keys.duplicated(keep=False)].drop_duplicates().to_dict("records")
        raise ValueError(f"Duplicate Case/Run keys found: {dupes[:5]}")

    for col in NUMERIC_SCORE_COLUMNS:
        vals = pd.to_numeric(df[col], errors="coerce")
        if vals.isna().any():
            raise ValueError(f"P2 numeric field contains invalid values: {col}")
    for col in ("failure_probability", "anomaly_score", "degradation_wear_score", "machine_health_score"):
        vals = pd.to_numeric(df[col], errors="coerce")
        if ((vals < 0) | (vals > 100)).any():
            raise ValueError(f"P2 score out of range 0-100: {col}")
    return df


def get_p2_machine_intelligence(case_id: int, run: int, p2_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    df = load_p2() if p2_df is None else p2_df
    mask = (df["case_id"].astype(int) == int(case_id)) & (df["run"].astype(int) == int(run))
    hit = df.loc[mask]
    if hit.empty:
        raise ValueError(f"P2 record not found for Case {case_id} / Run {run}.")
    if len(hit) != 1:
        raise ValueError(f"Expected one P2 record for Case {case_id} / Run {run}; found {len(hit)}.")
    row = hit.iloc[0]
    risk = float(row["failure_probability"])
    return {
        "machine_id": str(row["machine_id"]),
        "timestamp": str(row["timestamp"]),
        "case_id": int(row["case_id"]),
        "run": int(row["run"]),
        "prototype_failure_risk_index": risk,
        "machine_risk_0_100": risk,
        "risk_index": risk,  # compatibility for older internal scripts
        "anomaly_score": float(row["anomaly_score"]),
        "degradation_wear_score": float(row["degradation_wear_score"]),
        "wear_score": float(row["degradation_wear_score"]),  # compatibility
        "machine_health_score": float(row["machine_health_score"]),
        "health_score": float(row["machine_health_score"]),  # compatibility
        "health_status": str(row["health_status"]),
        "p2_production_bottleneck_risk": row["production_bottleneck_risk"],
        "p2_maintenance_priority": row["maintenance_priority"],
        "maintenance_priority": row["maintenance_priority"],
        "top_risk_factors": str(row["top_risk_factors"]),
        "feature_contributions": str(row["feature_contributions"]),
        "recommended_action": str(row["recommended_action"]),
        "VB_mm_observed": row["VB_mm_observed"],
        "VB_mm_estimated": row["VB_mm_estimated"],
        "VB_source": str(row["VB_source"]),
        "data_quality_flag": str(row["data_quality_flag"]),
        "source": "Frozen machine-intelligence output",
        "risk_semantics": "Prototype Failure Risk Index; not calibrated probability",
    }


def load_representative_confirmed(p2_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Return the three frozen representative Case/Run records used in rehearsal."""
    df = load_p2() if p2_df is None else p2_df
    wanted = [(13, 4), (15, 3), (4, 6)]
    rows = []
    for case_id, run in wanted:
        row = get_p2_machine_intelligence(case_id, run, df)
        rows.append({
            "Stage": "LOW" if case_id == 13 else ("MEDIUM" if case_id == 15 else "GOLDEN DEMO"),
            "Case/Run": f"{case_id}/{run}",
            "Risk": row["prototype_failure_risk_index"],
            "Anomaly": row["anomaly_score"],
            "Wear": row["degradation_wear_score"],
            "Health": row["machine_health_score"],
            "Health Status": row["health_status"],
            "VB Source": row["VB_source"],
            "Data Quality": row["data_quality_flag"],
        })
    return pd.DataFrame(rows)

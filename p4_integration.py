"""
FactoryMind - Operational + Decarbonization Intelligence
=========================================================
Transforms one exact machine-intelligence record into operational context,
What-If analysis and explicitly labelled carbon scenario estimates.
"""
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
METADATA_CSV = ROOT / "data" / "FactoryMind_Feature_Engineering.csv"
_FEATURE_DF = None


def load_feature_metadata(path: Optional[Path] = None) -> pd.DataFrame:
    global _FEATURE_DF
    p = Path(path) if path is not None else METADATA_CSV
    if _FEATURE_DF is None or path is not None:
        if not p.exists():
            raise FileNotFoundError(f"Feature metadata not found: {p}")
        df = pd.read_csv(p)
        for c in ("case_id", "run"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
        if df[["case_id", "run"]].isna().any().any():
            raise ValueError("Feature metadata contains invalid Case/Run keys.")
        if df[["case_id", "run"]].duplicated().any():
            raise ValueError("Feature metadata contains duplicate Case/Run keys.")
        _FEATURE_DF = df
    return _FEATURE_DF


def _bounded(value: float) -> float:
    value = float(value)
    if not 0 <= value <= 100:
        raise ValueError(f"Score must be between 0 and 100: {value}")
    return value


def _selected_features(case_id: int, run: int) -> pd.Series:
    df = load_feature_metadata()
    hit = df[(df["case_id"].astype(int) == int(case_id)) & (df["run"].astype(int) == int(run))]
    if hit.empty:
        raise ValueError(f"No feature metadata for Case {case_id} / Run {run}.")
    return hit.iloc[0]


def compute_operational_criticality(
    material_code: int,
    doc_mm: float,
    feed_mm_rev: float,
    has_backup: bool,
    dependency_override: Optional[float] = None,
    backup_override: Optional[float] = None,
    priority_override: Optional[float] = None,
) -> Dict[str, Any]:
    weights = {"dependency":0.30,"backup":0.25,"priority":0.20,"line_position":0.15,"throughput":0.10}
    c_dep = _bounded(dependency_override) if dependency_override is not None else (85.0 if int(material_code) == 2 else 45.0)
    c_backup = _bounded(backup_override) if backup_override is not None else (25.0 if has_backup else 90.0)
    c_priority = _bounded(priority_override) if priority_override is not None else (85.0 if int(material_code) == 2 else 45.0)
    c_line = 80.0 if float(doc_mm) >= 1.5 else 50.0
    mrr_factor = (float(doc_mm) / 1.5) * (float(feed_mm_rev) / 0.5)
    c_throughput = min(100.0, max(20.0, mrr_factor * 80.0))
    total = round(sum((
        weights["dependency"]*c_dep,
        weights["backup"]*c_backup,
        weights["priority"]*c_priority,
        weights["line_position"]*c_line,
        weights["throughput"]*c_throughput,
    )), 1)
    if total >= 75: tier = "Tier 1: Vital Bottleneck"
    elif total >= 50: tier = "Tier 2: High Operational Impact"
    elif total >= 30: tier = "Tier 3: Moderate Impact"
    else: tier = "Tier 4: Buffered / Low Impact"
    return {
        "operational_criticality": total,
        "criticality_tier": tier,
        "component_scores": {"dependency":round(c_dep,1),"backup":round(c_backup,1),"priority":round(c_priority,1),"line_position":round(c_line,1),"throughput":round(c_throughput,1)},
        "weights": weights,
    }


def compute_pbri(risk_index_0_100: float, operational_criticality_0_100: float) -> Dict[str, Any]:
    mr, oc = _bounded(risk_index_0_100), _bounded(operational_criticality_0_100)
    score = round((mr * oc) / 100.0, 1)
    if score >= 80: band, desc = "CRITICAL", "Line-stoppage threat - immediate operational response indicated."
    elif score >= 60: band, desc = "HIGH", "Severe bottleneck exposure - prepare mitigation and rerouting."
    elif score >= 30: band, desc = "MODERATE", "Elevated exposure - planned operational response is indicated."
    else: band, desc = "LOW", "Nominal exposure - continue standard operating checks."
    return {"pbri_score":score,"pbri_band":band,"pbri_description":desc}


def determine_maintenance_priority(risk_index_0_100: float, criticality_0_100: float, has_backup: bool=False, backup_available: Optional[bool]=None) -> Dict[str, Any]:
    if backup_available is not None: has_backup = backup_available
    risk, crit = _bounded(risk_index_0_100), _bounded(criticality_0_100)
    if risk < 45:
        return {"maintenance_priority":"Routine","response_window":"Standard Autonomous Inspection","action":"Continue routine inspection and monitoring; no immediate line intervention indicated."}
    if risk >= 70 and crit >= 60 and not has_backup:
        return {"maintenance_priority":"Emergency","response_window":"Immediate (< 1 hour)","action":"Halt or safely pause at the next safe retract point and dispatch maintenance with replacement tooling."}
    if risk >= 70 and crit >= 60 and has_backup:
        return {"maintenance_priority":"Scheduled High","response_window":"Within Shift (< 4 hours)","action":"Reroute the affected lot to the standby cell and service the degraded tool before shift end."}
    if risk >= 70 and crit < 50 and has_backup:
        return {"maintenance_priority":"High machine risk, lower operational impact","response_window":"Planned Window (< 24 hours)","action":"Use standby capacity and schedule service in the next planned maintenance window without stopping the line."}
    if risk >= 45 and crit >= 70 and not has_backup:
        return {"maintenance_priority":"Elevated Preventive","response_window":"Within 8 hours","action":"Pre-stage replacement tooling and verify wear before heavy cutting continues."}
    return {"maintenance_priority":"Planned","response_window":"Next Scheduled Maintenance Window","action":"Schedule preventive servicing and log the condition for follow-up."}


def simulate_what_if(risk_index_0_100: float, criticality_0_100: float, has_backup: bool, buffer_minutes: float=30.0, rerouting_efficiency_pct: float=75.0) -> Dict[str, Any]:
    risk, crit = _bounded(risk_index_0_100), _bounded(criticality_0_100)
    buf, reroute = float(buffer_minutes), float(rerouting_efficiency_pct)
    if not 5 <= buf <= 120: raise ValueError("Buffer minutes must be between 5 and 120.")
    if not 0 <= reroute <= 100: raise ValueError("Rerouting efficiency must be between 0 and 100%.")
    if not has_backup and crit >= 60 and risk >= 60:
        exposure, starvation = "CRITICAL", "HIGH"
        impact = f"LINE STOPPAGE - downstream operations would exhaust the displayed {buf:.0f}-minute buffer."
    elif not has_backup and crit >= 50:
        exposure = "HIGH"
        starvation = "HIGH" if buf < 45 else "MEDIUM"
        impact = f"BUFFER DEPLETION - downstream buffer would be exhausted in {buf:.0f} minutes."
    elif has_backup and risk >= 70:
        exposure, starvation = "MODERATE", "LOW"
        impact = f"REROUTING ENGAGED - {reroute:.0f}% throughput retained through the standby scenario."
    else:
        exposure, starvation = "LOW", "LOW"
        impact = "LOW OPERATIONAL IMPACT - available buffers or alternate routing absorb the scenario."
    return {"buffer_minutes":buf,"rerouting_efficiency_pct":reroute,"downstream_starvation_risk":starvation,"bottleneck_exposure_rating":exposure,"line_status_impact":impact}


def compute_decarbonization_metrics(case_id: int, run: int, runtime_min: Optional[float]=None, power_kw: Optional[float]=None, efficiency_gain_pct: float=15.0, grid_factor: float=0.716) -> Dict[str, Any]:
    row = _selected_features(case_id, run)
    runtime = float(row["elapsed_time_min"]) if runtime_min is None else float(runtime_min)
    if runtime < 0: raise ValueError("Runtime must be non-negative.")
    if power_kw is None:
        if "power_kw_demo" in row.index and pd.notna(row.get("power_kw_demo")):
            power = float(row["power_kw_demo"]); source = "stored scenario metadata"
        else:
            power = 7.01 if float(row["DOC_mm"]) >= 1.5 else 5.0; source = "prototype power scenario profile"
    else:
        power = float(power_kw); source = "explicit scenario input"
    if power < 0 or grid_factor < 0: raise ValueError("Power and grid factor must be non-negative.")
    gain = max(0.0, min(100.0, float(efficiency_gain_pct))) / 100.0
    energy = round((runtime/60.0)*power, 3)
    co2e = round(energy*float(grid_factor), 3)
    saved = round(energy*gain, 3)
    avoided = round(saved*float(grid_factor), 3)
    return {
        "runtime_min": runtime, "power_kw_scenario": power, "power_source": source,
        "grid_factor_kgco2e_per_kwh": float(grid_factor), "energy_kwh_scenario": energy,
        "co2e_kg_scenario": co2e,
        "efficiency_scenario": {"efficiency_gain_pct":float(efficiency_gain_pct),"energy_saved_kwh":saved,"co2e_avoided_kg":avoided,"action_trigger":"Inspect/replace worn tooling and reassess the energy scenario."},
        "provenance":"SCENARIO ESTIMATE - power is not a measured plant kWh meter",
        "assumptions":[f"Runtime source: feature-engineering elapsed time for Case {case_id} / Run {run}.",f"Power source: {source}.",f"Grid factor: {grid_factor} kgCO2e/kWh (CEA FY2022-23 benchmark).",f"Efficiency scenario assumes {float(efficiency_gain_pct):.0f}% reduction in modeled energy use."],
    }


def get_p4_operational_intelligence(p2: Dict[str, Any], has_backup: bool=False, buffer_minutes: float=30.0, rerouting_efficiency_pct: float=75.0, dependency_override: Optional[float]=None, backup_override: Optional[float]=None, priority_override: Optional[float]=None, efficiency_gain_pct: float=15.0) -> Dict[str, Any]:
    case_id, run = int(p2["case_id"]), int(p2["run"])
    risk = float(p2["prototype_failure_risk_index"])
    row = _selected_features(case_id, run)
    required = ["material_code","DOC_mm","feed_mm_rev","elapsed_time_min"]
    missing = [c for c in required if pd.isna(row.get(c))]
    if missing: raise ValueError(f"Missing feature metadata for Case {case_id} / Run {run}: {missing}")
    material_code, doc, feed, elapsed = int(row["material_code"]), float(row["DOC_mm"]), float(row["feed_mm_rev"]), float(row["elapsed_time_min"])
    crit = compute_operational_criticality(material_code, doc, feed, has_backup, dependency_override, backup_override, priority_override)
    pbri = compute_pbri(risk, crit["operational_criticality"])
    maint = determine_maintenance_priority(risk, crit["operational_criticality"], has_backup)
    what_if = simulate_what_if(risk, crit["operational_criticality"], has_backup, buffer_minutes, rerouting_efficiency_pct)
    base_crit = compute_operational_criticality(material_code, doc, feed, False)["operational_criticality"]
    base_pbri = compute_pbri(risk, base_crit)
    base_maint = determine_maintenance_priority(risk, base_crit, False)
    decarb = compute_decarbonization_metrics(case_id, run, runtime_min=elapsed, efficiency_gain_pct=efficiency_gain_pct)
    return {
        "case_id":case_id,"run":run,
        "traceability":{"selected_record":f"Case {case_id} / Run {run}","consumes_exact_machine_record":True,"manual_machine_risk_editing":False},
        "machine_parameters":{"material_code":material_code,"material_name":"Aerospace Stainless Steel" if material_code==2 else "Cast Iron","depth_of_cut_mm":doc,"feed_mm_rev":feed,"runtime_min":elapsed},
        "operational_criticality":crit["operational_criticality"],"criticality_tier":crit["criticality_tier"],"criticality_components":crit["component_scores"],"criticality_weights":crit["weights"],
        "pbri_score":pbri["pbri_score"],"pbri_band":pbri["pbri_band"],"pbri_description":pbri["pbri_description"],
        "maintenance_priority":maint["maintenance_priority"],"response_window":maint["response_window"],"recommended_action":maint["action"],
        "what_if":what_if,
        "baseline_comparison":{"criticality":base_crit,"pbri":base_pbri["pbri_score"],"pbri_band":base_pbri["pbri_band"],"priority":base_maint["maintenance_priority"],"response_window":base_maint["response_window"]},
        "decarbonization":decarb,
    }

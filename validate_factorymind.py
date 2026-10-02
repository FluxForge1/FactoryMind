"""FactoryMind deterministic validation suite.

This suite validates the current GitHub-ready package against the frozen
machine-intelligence and operational-intelligence contracts used by the demo.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DATA = ROOT / "data"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from p2_integration import get_p2_machine_intelligence, load_p2  # noqa: E402
from p4_integration import (  # noqa: E402
    compute_decarbonization_metrics,
    compute_operational_criticality,
    compute_pbri,
    determine_maintenance_priority,
    get_p4_operational_intelligence,
    load_feature_metadata,
    simulate_what_if,
)


def check(label: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"[FAIL] {label}. {detail}".strip())
    print(f"[PASS] {label}" + (f" — {detail}" if detail else ""))


def main() -> None:
    print("=" * 72)
    print("FACTORYMIND — GITHUB PACKAGE VALIDATION")
    print("=" * 72)

    # 1. Files / keys
    p2 = load_p2()
    features = load_feature_metadata(DATA / "FactoryMind_Feature_Engineering.csv")
    check("P2 dataset size", len(p2) == 167, f"rows={len(p2)}")
    check("Feature dataset size", len(features) == 167, f"rows={len(features)}")
    check("P2 Case/Run uniqueness", not p2[["case_id", "run"]].duplicated().any())
    check("Feature Case/Run uniqueness", not features[["case_id", "run"]].duplicated().any())

    # 2. Golden / low / medium frozen records
    golden = get_p2_machine_intelligence(4, 6, p2)
    low = get_p2_machine_intelligence(13, 4, p2)
    med = get_p2_machine_intelligence(15, 3, p2)
    check("Golden risk", golden["risk_index"] == 81.1)
    check("Golden anomaly", golden["anomaly_score"] == 81.4)
    check("Golden wear", golden["wear_score"] == 81.6)
    check("Golden health", golden["health_score"] == 18.9)
    check("Low rehearsal record", (low["risk_index"], low["health_score"], low["wear_score"]) == (21.0, 79.0, 8.5))
    check("Medium rehearsal record", (med["risk_index"], med["health_score"], med["wear_score"]) == (49.8, 50.2, 40.0))

    # 3. Criticality
    golden_features = features[(features.case_id == 4) & (features.run == 6)].iloc[0]
    no_backup = compute_operational_criticality(
        int(golden_features["material_code"]),
        float(golden_features["DOC_mm"]),
        float(golden_features["feed_mm_rev"]),
        False,
    )
    backup = compute_operational_criticality(
        int(golden_features["material_code"]),
        float(golden_features["DOC_mm"]),
        float(golden_features["feed_mm_rev"]),
        True,
    )
    check("Golden criticality without backup", no_backup["operational_criticality"] == 61.0)
    check("Golden criticality with backup", backup["operational_criticality"] == 44.8)

    # 4. PBRI
    check("Golden PBRI without backup", compute_pbri(81.1, 61.0)["pbri_score"] == 49.5)
    check("Golden PBRI with backup", compute_pbri(81.1, 44.8)["pbri_score"] == 36.3)
    check("PBRI formula", compute_pbri(50.0, 50.0)["pbri_score"] == 25.0)

    # 5. Maintenance decisions
    a = determine_maintenance_priority(21.0, 30.0, has_backup=True)
    b = determine_maintenance_priority(81.1, 44.8, has_backup=True)
    c = determine_maintenance_priority(81.1, 75.0, has_backup=True)
    d = determine_maintenance_priority(81.1, 61.0, has_backup=False)
    check("Situation A priority", a["maintenance_priority"] == "Routine")
    check("Situation B priority", b["maintenance_priority"] == "High machine risk, lower operational impact")
    check("Situation C priority", c["maintenance_priority"] == "Scheduled High")
    check("Situation D priority", d["maintenance_priority"] == "Emergency")

    # 6. What-If
    base = get_p4_operational_intelligence(golden, has_backup=False, buffer_minutes=30.0, rerouting_efficiency_pct=0.0)
    alt = get_p4_operational_intelligence(golden, has_backup=True, buffer_minutes=30.0, rerouting_efficiency_pct=75.0)
    check("What-If baseline criticality", base["operational_criticality"] == 61.0)
    check("What-If backup criticality", alt["operational_criticality"] == 44.8)
    check("What-If risk invariance", base["case_id"] == alt["case_id"] == 4 and golden["risk_index"] == 81.1)
    check("What-If no-backup exposure", simulate_what_if(81.1, 61.0, False, 30, 0)["bottleneck_exposure_rating"] == "CRITICAL")
    check("What-If backup exposure", simulate_what_if(81.1, 44.8, True, 30, 75)["bottleneck_exposure_rating"] == "MODERATE")

    # 7. Decarbonisation arithmetic / provenance
    decarb = compute_decarbonization_metrics(4, 6, runtime_min=34.0, efficiency_gain_pct=15.0, grid_factor=0.716)
    check("Runtime source", decarb["runtime_min"] == 34.0)
    check("Scenario power", decarb["power_kw_scenario"] == 7.01)
    check("Scenario energy", decarb["energy_kwh_scenario"] == 3.972)
    check("Scenario CO2e", decarb["co2e_kg_scenario"] == 2.844)
    check("Scenario avoided CO2e", decarb["efficiency_scenario"]["co2e_avoided_kg"] == 0.427)
    check("Carbon provenance", "SCENARIO ESTIMATE" in decarb["provenance"])

    # 8. Data-quality semantics
    check("Golden wear source", golden["VB_source"] == "observed")
    check("Golden data quality", golden["data_quality_flag"] == "usable")
    check("Risk semantics guardrail", golden["risk_semantics"] == "Prototype Failure Risk Index; not calibrated probability")

    # 9. Stale-selector sequence
    sequence = [(4, 6), (13, 4), (15, 3), (4, 6)]
    states = [get_p2_machine_intelligence(c, r, p2) for c, r in sequence]
    check("Atomic Case/Run sequence", [(s["case_id"], s["run"]) for s in states] == sequence)
    check("Golden return values", (states[-1]["risk_index"], states[-1]["health_score"], states[-1]["wear_score"]) == (81.1, 18.9, 81.6))

    # 10. Package-level path checks
    required = [
        ROOT / "app.py",
        ROOT / "requirements.txt",
        ROOT / "README.md",
        ROOT / ".gitignore",
        ROOT / "LICENSE",
        SRC / "p2_integration.py",
        SRC / "p4_integration.py",
        SRC / "decarbonization.py",
        DATA / "FactoryMind_P2_Final_ys.csv",
        DATA / "FactoryMind_Feature_Engineering.csv",
        ROOT / "presentation" / "FactoryMind_Final_Submission_12Slides_FINAL.pptx",
    ]
    check("Required repository files present", all(p.exists() for p in required))

    print("=" * 72)
    print("FINAL RESULT: FACTORYMIND VALIDATION PASSED")
    print("=" * 72)


if __name__ == "__main__":
    main()

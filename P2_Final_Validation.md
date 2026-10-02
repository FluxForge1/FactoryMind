# FACTORYMIND — DAY 10 — P2 MACHINE INTELLIGENCE | FINAL VALIDATION & FREEZE

**Status:** Frozen & Integration-Ready  
**Handoff:** P2 → P3 / P4 (consume values directly; do not recalculate)

---

## Mission
Freeze the machine-intelligence layer so P3 and P4 can integrate it without manually changing or independently recalculating P2 values.

---

## P2 Pipeline
```
Machine / Run → Input Signals → Anomaly + Wear → Prototype Failure Risk Index
→ Machine Health → Health Status → Top Risk Factors / WHY → Recommended Action
→ Data Quality → P4
```

---

## 1. Frozen P2 Output Schema

| Field | Purpose |
|:---|:---|
| `case_id` | Selected case |
| `run` | Selected run |
| `machine_id` | Machine identity |
| `failure_risk_index` | Prototype machine-risk indicator |
| `anomaly_score` | Degree of unusual machine behavior |
| `degradation_wear_score` | Evidence of wear/degradation |
| `machine_health_score` | Overall machine condition |
| `health_status` | Human-readable condition |
| `top_risk_factors` | Main displayed reasons for risk |
| `recommended_action` | Suggested machine-level response |
| `data_quality` | Quality/completeness status |

---

## 2. Metric Definitions & Required Terminology

- **Prototype Failure Risk Index:** Overall machine-condition risk indicator used by the prototype.  
  > **Required wording:** *“The Prototype Failure Risk Index is a prototype operational risk indicator; it is not a calibrated probability of failure.”*

- **Anomaly Score:** Indicates how unusual the observed machine/signal pattern is.

- **Wear / Degradation:** Represents degradation/wear evidence used by the machine-intelligence layer.

- **Machine Health:** Machine-condition indicator; in the established prototype, Health = 100 − Risk.

- **Health Status:** Human-readable interpretation of machine condition.

- **Top Risk Factors:** Main displayed factors explaining the risk assessment. Do **not** call them SHAP values unless genuine model-native SHAP attribution exists.

- **Data Quality:** Communicates completeness and missing/suspect measurement information.

---

## 3. Golden Demo — Case 4 / Run 6

| P2 Metric | Confirmed Value |
|:---|:---:|
| **Prototype Failure Risk Index** | **81.1** |
| **Anomaly Score** | **81.4** |
| **Wear / Degradation** | **81.6** |
| **Machine Health** | **18.9** |

> **Required judge wording:** *“81.1 is the Prototype Failure Risk Index, a prototype operational risk indicator; it is not a calibrated probability of failure.”*

---

## 4. Three-Case Validation

| Test | Purpose | Checks |
|:---|:---|:---|
| **Case 13 / Run 4** | LOW | Risk 21.0, Anomaly 41.3, Wear 8.5, Health 79.0, Status Watch |
| **Case 15 / Run 3** | MEDIUM | Risk 49.8, Anomaly 59.9, Wear 40.0, Health 50.2, Status Degraded |
| **Case 4 / Run 6** | HIGH / GOLDEN | Risk 81.1, Anomaly 81.4, Wear 81.6, Health 18.9, Status Critical |

**Rule:** Do not invent or manually type Low/Medium numeric values. They must come directly from the frozen P2 dataset/output.

---

## 5. Stale-Value Stress Test
**Sequence:** Case 4 / Run 6 → Case 13 / Run 4 → Case 15 / Run 3 → Case 4 / Run 6  

After every switch, verify `case_id`, `run`, `machine_id`, risk, anomaly, wear, health, health_status, top_risk_factors, recommended_action, and data_quality all refresh together.

**Critical return test:** Case 4 / Run 6 must restore **81.1 / 81.4 / 81.6 / 18.9**.

---

## 6. P2 → P4 Handoff
- **P2 asks:** *“What is happening to the machine?”*
- **P4 asks:** *“How important is that machine to factory operations?”*
- **Core Principle:** Machine Risk ≠ Operational Criticality ≠ PBRI ≠ Maintenance Priority.
- P3 displays P2 outputs and must not independently rebuild the machine-risk calculation.

---

## 7. Scientific / Claims QA

| Claim | Status |
|:---|:---|
| “81.1% chance of failure” | ❌ **Not allowed** |
| “Guaranteed failure” | ❌ **Not allowed** |
| “Exact failure prediction” | ❌ **Not allowed** |
| “Exact remaining useful life” | ❌ **Not allowed** |
| “SHAP explanation” | ❌ **Unless genuine SHAP exists** |
| “Prototype Failure Risk Index” | ✅ **Correct** |
| “Top Risk Factors” | ✅ **Correct** |
| “Prototype operational risk indicator” | ✅ **Correct** |

---

## 8. Missing / Suspect Data Handling
If VB or another required measurement is missing, do **not** create a fake observed value. Flag the data-quality limitation and use only supported available evidence.

> **Judge answer:** *“If a required measurement is missing, we don't present a fabricated value as observed data. We flag the data-quality limitation and use only the supported available evidence.”*

---

## 9. P2 Rapid-Fire Defense
- **Q: What does 81.1 mean?**  
  *A: It is the Prototype Failure Risk Index, a prototype operational risk indicator; it is not a calibrated probability of failure.*

- **Q: Why isn't anomaly the same as wear?**  
  *A: Anomaly represents unusual machine behaviour, while wear represents degradation evidence.*

- **Q: How is health different from risk?**  
  *A: Risk expresses machine-condition concern; health expresses the resulting condition. In our prototype, Health = 100 − Risk.*

- **Q: Why aren't Top Risk Factors called SHAP values?**  
  *A: Because the current explanation layer does not demonstrate genuine model-native SHAP attribution.*

- **Q: What happens if data is missing?**  
  *A: We flag the data-quality limitation instead of presenting a fabricated measurement.*

- **Q: What dataset powers P2?**  
  *A: The prototype machine-intelligence layer uses the NASA Milling Dataset and its experimental milling/process data.*

- **Q: Why isn't P2 risk enough?**  
  *A: Machine risk describes machine condition, but not how important that machine is to factory operations.*

- **Q: Can this be deployed directly in a real factory?**  
  *A: The prototype demonstrates the decision architecture. Real deployment requires validated plant-specific sensor data, calibration, operational integration, monitoring and industrial validation.*

---

## 10. Final P2 Freeze Checklist
- [x] Dataset / record selection verified
- [x] Case + Run identify the selected record
- [x] No manual CSV editing during demo
- [x] Risk verified (81.1)
- [x] Anomaly verified (81.4)
- [x] Wear verified (81.6)
- [x] Health verified (18.9)
- [x] Health Status verified (Critical)
- [x] Top Risk Factors verified
- [x] Recommended Action verified
- [x] Data Quality verified
- [x] Case 4 / Run 6 Golden values confirmed
- [x] Case switching / stale-value test completed
- [x] P2 → P4 handoff defined
- [x] No calibrated-probability claim
- [x] No guaranteed-failure claim
- [x] No exact-RUL claim
- [x] No unsupported SHAP claim

---

## 11. Final P2 Handoff Statement
> **“P2 is frozen. For each Case/Run, the machine-intelligence layer provides Risk, Anomaly, Wear, Health, Health Status, Top Risk Factors, Recommended Action and Data Quality. Case 4 / Run 6 is confirmed at Risk 81.1, Anomaly 81.4, Wear 81.6 and Health 18.9. The Prototype Failure Risk Index is an operational prototype indicator, not a calibrated failure probability. P4 should consume these outputs directly and add operational context rather than recalculating machine intelligence.”**

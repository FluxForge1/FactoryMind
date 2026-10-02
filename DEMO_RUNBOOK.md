# FactoryMind — 3-minute demo runbook

## 1. Establish the machine state

Select **Case 4 / Run 6** and point to:

- Risk Index: 81.1 (prototype indicator)
- Anomaly: 81.4
- Wear: 81.6
- Health: 18.9 / Critical

Say: **“This tells me the machine state. It does not yet tell me the factory response.”**

## 2. Show the business consequence

With backup unavailable:

- Criticality = 61.0
- PBRI = 49.5
- Priority = Emergency
- Response window = Immediate (< 1 hour)

Say: **“Operational context turns the same machine risk into an urgent factory decision.”**

## 3. Run the What-If

Enable backup. The machine state must remain the same.

The dashboard should show:

- Risk = 81.1 (unchanged)
- Criticality = 44.8
- PBRI = 36.3
- Priority = High machine risk, lower operational impact
- Response window = Planned Window (< 24 hours)

Say: **“The machine did not become healthier. The factory became more resilient.”**

## 4. Close with carbon

Open Decarbonisation Intelligence and explain the evidence classes:

- measured runtime,
- scenario power / grid assumptions,
- derived energy / carbon values.

For the current golden scenario:

- 34 min runtime
- 7.01 kW scenario power
- 3.972 kWh/run
- 2.844 kgCO₂e/run
- 15% modeled efficiency lever
- 0.427 kgCO₂e/run avoided in the scenario

Finish with: **“We keep uncertainty visible so the same decision center can move from prototype proxies to plant data.”**

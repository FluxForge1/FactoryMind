"""FactoryMind Decarbonization Intelligence — transparent scenario module.

This module intentionally uses explicit scenario assumptions because the NASA
Milling source package does not provide a validated factory electricity meter,
plant energy bill, or site-specific grid emission factor.

The selected run duration comes from the feature-engineering dataset. Energy
and CO2e are scenario estimates derived from operator-provided assumptions.
"""
from __future__ import annotations

from typing import Any, Dict


def compute_decarbonization(
    elapsed_time_min: float,
    machine_power_kw: float = 5.0,
    grid_emission_factor_kg_per_kwh: float = 0.70,
    efficiency_opportunity_pct: float = 10.0,
    backup_available: bool = False,
    rerouting_efficiency_pct: float = 75.0,
    backup_power_fraction: float = 0.85,
) -> Dict[str, Any]:
    """Return transparent energy/CO2e scenario estimates for one run.

    Base case:
      energy_kwh = assumed_machine_power_kw * measured_run_time_hours
      co2e_kg   = energy_kwh * assumed_grid_factor

    Efficiency scenario:
      applies an operator-selected percentage reduction to base energy.

    Backup scenario:
      estimates additional energy exposure if a standby machine is run for
      the rerouted share of the run at a stated standby-power fraction.
      This is explicitly a scenario estimate, not measured consumption.
    """
    t_min = max(0.0, float(elapsed_time_min))
    power_kw = max(0.0, float(machine_power_kw))
    ef = max(0.0, float(grid_emission_factor_kg_per_kwh))
    eff = min(100.0, max(0.0, float(efficiency_opportunity_pct)))
    reroute = min(100.0, max(0.0, float(rerouting_efficiency_pct)))
    backup_frac = min(2.0, max(0.0, float(backup_power_fraction)))

    hours = t_min / 60.0
    baseline_kwh = power_kw * hours
    baseline_co2e = baseline_kwh * ef

    efficient_kwh = baseline_kwh * (1.0 - eff / 100.0)
    efficient_co2e = efficient_kwh * ef
    savings_kwh = baseline_kwh - efficient_kwh
    savings_co2e = baseline_co2e - efficient_co2e

    backup_kwh = 0.0
    backup_co2e = 0.0
    if backup_available:
        backup_kwh = baseline_kwh * (reroute / 100.0) * backup_frac
        backup_co2e = backup_kwh * ef

    return {
        "elapsed_time_min": round(t_min, 2),
        "elapsed_time_source": "MEASURED RUN DURATION (feature dataset)",
        "machine_power_kw": round(power_kw, 3),
        "machine_power_source": "SCENARIO ASSUMPTION (operator input)",
        "grid_emission_factor_kg_per_kwh": round(ef, 3),
        "grid_factor_source": "SCENARIO ASSUMPTION (site/grid dependent)",
        "baseline": {
            "energy_kwh": round(baseline_kwh, 3),
            "co2e_kg": round(baseline_co2e, 3),
            "co2e_kg_per_hour": round(power_kw * ef, 3),
        },
        "efficiency_scenario": {
            "improvement_pct": round(eff, 1),
            "energy_kwh": round(efficient_kwh, 3),
            "co2e_kg": round(efficient_co2e, 3),
            "energy_saved_kwh": round(savings_kwh, 3),
            "co2e_avoided_kg": round(savings_co2e, 3),
        },
        "backup_scenario": {
            "backup_available": bool(backup_available),
            "rerouting_efficiency_pct": round(reroute, 1),
            "backup_power_fraction": round(backup_frac, 2),
            "additional_energy_kwh": round(backup_kwh, 3),
            "additional_co2e_kg": round(backup_co2e, 3),
        },
        "provenance": {
            "measured": ["elapsed_time_min"],
            "scenario_assumptions": [
                "machine_power_kw",
                "grid_emission_factor_kg_per_kwh",
                "efficiency_opportunity_pct",
                "rerouting_efficiency_pct",
                "backup_power_fraction",
            ],
        },
        "guardrail": "Scenario CO2e estimate only; not a measured plant emissions inventory.",
    }

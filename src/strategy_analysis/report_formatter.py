from typing import Dict, Any


# =========================================================
# STRATEGY REPORT FORMATTER
# =========================================================

def format_strategy_report(report_data: Dict[str, Any]) -> str:
    """
    Convert strategy report dictionary into a readable text report.

    Parameters
    ----------
    report_data : dict
        Output from strategy_report module.

    Returns
    -------
    Formatted strategy report string
    """

    if not report_data:
        return "No strategy report available."

    pit_laps = report_data.get("pit_laps", [])
    compounds = report_data.get("compounds", [])
    total_stops = report_data.get("total_stops")
    avg_stint = report_data.get("average_stint_length")
    expected_time = report_data.get("expected_race_time")
    risk = report_data.get("risk_spread")

    lines = []

    lines.append("AI STRATEGY REPORT")
    lines.append("------------------")
    lines.append("")

    lines.append(f"Total Stops: {total_stops}")
    lines.append("")

    lines.append("Pit Stops")

    for lap, compound in zip(pit_laps, compounds):
        lines.append(f"Lap {lap} → {compound}")

    lines.append("")

    if avg_stint is not None:
        lines.append(f"Average Stint Length: {avg_stint:.1f} laps")

    if expected_time is not None:
        lines.append(f"Expected Race Time: {expected_time:.2f}")

    if risk is not None:
        lines.append(f"Risk Spread: ±{risk:.2f}")

    return "\n".join(lines)
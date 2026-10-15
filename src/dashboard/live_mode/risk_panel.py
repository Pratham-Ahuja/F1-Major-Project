import streamlit as st
import plotly.graph_objects as go
import numpy as np


# =========================================================
# RISK PANEL — Monte Carlo Outcome Visualization
# =========================================================

def render_risk_panel(mc_results):
    """
    Render Monte Carlo risk visualization panel.

    Supports BOTH formats:
    1) dict
    2) RiskMetrics object
    """

    st.subheader("📉 Monte Carlo Risk Analysis")

    if mc_results is None:
        st.warning("Monte Carlo results not available")
        return

    # -----------------------------------------------------
    # HANDLE BOTH DICT AND OBJECT
    # -----------------------------------------------------

    if isinstance(mc_results, dict):

        outcomes = np.array(mc_results.get("outcomes", []))
        best_case = mc_results.get("best_case")
        expected_case = mc_results.get("expected_case")
        worst_case = mc_results.get("worst_case")
        risk_level = mc_results.get("risk_level", "UNKNOWN")

    else:
        # RiskMetrics object support
        outcomes = np.array(getattr(mc_results, "outcomes", []))
        best_case = getattr(mc_results, "best_case", None)
        expected_case = getattr(mc_results, "expected_case", None)
        worst_case = getattr(mc_results, "worst_case", None)
        risk_level = getattr(mc_results, "risk_level", "UNKNOWN")

    # -----------------------------------------------------

    if outcomes.size == 0:
        st.warning("No Monte Carlo samples found")
        return

    # -----------------------------------------------------
    # Compute statistics
    # -----------------------------------------------------

    mean_val = np.mean(outcomes)
    std_val = np.std(outcomes)

    # -----------------------------------------------------
    # Histogram Distribution
    # -----------------------------------------------------

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            x=outcomes,
            nbinsx=30,
            marker_color="#3498db",
            opacity=0.75,
            name="Simulated Outcomes",
            hovertemplate="Outcome: %{x:.2f}<br>Count: %{y}<extra></extra>"
        )
    )

    # -----------------------------------------------------
    # Reference Lines
    # -----------------------------------------------------

    if best_case is not None:
        fig.add_vline(
            x=best_case,
            line_dash="dash",
            line_color="green",
            annotation_text="Best Case",
            annotation_position="top left"
        )

    if expected_case is not None:
        fig.add_vline(
            x=expected_case,
            line_dash="dash",
            line_color="orange",
            annotation_text="Expected",
            annotation_position="top left"
        )

    if worst_case is not None:
        fig.add_vline(
            x=worst_case,
            line_dash="dash",
            line_color="red",
            annotation_text="Worst Case",
            annotation_position="top left"
        )

    fig.add_vline(
        x=mean_val,
        line_color="black",
        line_width=2,
        annotation_text="Mean"
    )

    fig.update_layout(
        title="Monte Carlo Outcome Distribution",
        xaxis_title="Race Outcome Metric",
        yaxis_title="Frequency",
        bargap=0.05,
        height=380
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------
    # Summary Metrics
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Best Case", f"{best_case:.2f}" if best_case else "-")
    col2.metric("Expected", f"{expected_case:.2f}" if expected_case else "-")
    col3.metric("Worst Case", f"{worst_case:.2f}" if worst_case else "-")
    col4.metric("Std Dev", f"{std_val:.2f}")

    # -----------------------------------------------------
    # Risk Interpretation
    # -----------------------------------------------------

    st.markdown(
        f"""
        **Risk Level:** `{risk_level}`  

        **Interpretation**
        - Narrow distribution → Low uncertainty  
        - Wide distribution → High uncertainty  
        - Long right tail → Potential downside risk  
        """
    )
import streamlit as st


# =========================================================
# EVALUATION METRICS PANEL
# =========================================================

def render_evaluation_metrics(research_data: dict | None):
    """
    Render evaluation metrics panel for Research Mode.
    """

    st.subheader("📊 Model Evaluation Metrics")

    if research_data is None:

        st.info("No research data available yet.")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Accuracy", "N/A")

        with col2:
            st.metric("Precision", "N/A")

        with col3:
            st.metric("Recall", "N/A")

        with col4:
            st.metric("F1 Score", "N/A")

        return

    try:

        real_pit_laps = research_data.get("real_pit_laps", [])
        strategy_results = research_data.get("strategy_results", [])
        total_laps = research_data.get("total_laps", 0)

        # -----------------------------------------------------
        # Convert strategy experiments into predicted pit laps
        # -----------------------------------------------------

        predicted_pits = []

        for s in strategy_results:
            lap = s.get("pit_lap")
            if lap is not None:
                predicted_pits.append(lap)

        # -----------------------------------------------------
        # Confusion Matrix Components
        # -----------------------------------------------------

        TP = 0
        FP = 0
        FN = 0
        TN = 0

        for lap in range(1, total_laps + 1):

            real = lap in real_pit_laps
            pred = lap in predicted_pits

            if real and pred:
                TP += 1

            elif not real and pred:
                FP += 1

            elif real and not pred:
                FN += 1

            else:
                TN += 1

        # -----------------------------------------------------
        # Metric Calculations
        # -----------------------------------------------------

        if (TP + TN + FP + FN) == 0:
            accuracy = 0
        else:
            accuracy = (TP + TN) / (TP + TN + FP + FN)

        if (TP + FP) == 0:
            precision = 0
        else:
            precision = TP / (TP + FP)

        if (TP + FN) == 0:
            recall = 0
        else:
            recall = TP / (TP + FN)

        if (precision + recall) == 0:
            f1_score = 0
        else:
            f1_score = 2 * (precision * recall) / (precision + recall)

        # -----------------------------------------------------
        # Display Metrics
        # -----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Accuracy", f"{accuracy:.3f}")

        with col2:
            st.metric("Precision", f"{precision:.3f}")

        with col3:
            st.metric("Recall", f"{recall:.3f}")

        with col4:
            st.metric("F1 Score", f"{f1_score:.3f}")

    except Exception as e:

        st.warning("Evaluation metrics could not be computed.")
        st.error(str(e))
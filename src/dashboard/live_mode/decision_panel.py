import streamlit as st


# =========================================================
# DECISION PANEL — AI Strategy Recommendation
# =========================================================

def render_decision_panel(decision):

    st.subheader("🧠 AI Strategy Recommendation")

    if decision is None:
        st.warning("No decision available")
        return

    # -----------------------------------------------------
    # SAFE ATTRIBUTE ACCESS
    # -----------------------------------------------------

    action = getattr(decision, "action", "UNKNOWN")
    confidence = getattr(decision, "confidence", 0.0)
    risk_level = getattr(decision, "risk_level", "UNKNOWN")
    strategy_type = getattr(decision, "strategy_type", "STANDARD")
    explanation = getattr(decision, "explanation", "No explanation available")

    # -----------------------------------------------------
    # AI Recommendation
    # -----------------------------------------------------

    st.markdown(
        f"""
        ### **Action: `{action}`**
        """
    )

    # -----------------------------------------------------
    # Confidence Bar
    # -----------------------------------------------------

    confidence_value = min(max(confidence, 0.0), 1.0)

    st.progress(confidence_value)

    st.markdown(
        f"""
        **Confidence:** {confidence:.2f}  
        **Risk Level:** {risk_level}  
        **Strategy Mode:** {strategy_type}
        """
    )

    # -----------------------------------------------------
    # Explanation
    # -----------------------------------------------------

    st.markdown("### 📝 Explanation")

    st.info(explanation)

    st.divider()

    # =====================================================
    # HUMAN-IN-THE-LOOP SECTION
    # =====================================================

    st.markdown("### 👨‍🔧 Human-in-the-Loop Decision")

    st.markdown(
        "Did the engineer execute the AI recommendation?"
    )

    if "human_decision" not in st.session_state:
        st.session_state["human_decision"] = None

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # YES BUTTON
    # -----------------------------------------------------

    with col1:

        if st.button("✅ YES — Pit Executed"):

            st.session_state["human_decision"] = "y"

            if "race_state" in st.session_state:
                st.session_state["race_state"].human_decision = "y"

    # -----------------------------------------------------
    # NO BUTTON
    # -----------------------------------------------------

    with col2:

        if st.button("❌ NO — Stayed Out"):

            st.session_state["human_decision"] = "n"

            if "race_state" in st.session_state:
                st.session_state["race_state"].human_decision = "n"

    # -----------------------------------------------------
    # Display decision
    # -----------------------------------------------------

    if st.session_state["human_decision"] is not None:

        st.success(
            f"Human Decision Recorded: `{st.session_state['human_decision']}`"
        )

    else:

        st.info("Waiting for human confirmation...")
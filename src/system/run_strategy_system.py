# =========================================================
# F1 AI STRATEGY SYSTEM — MAIN RUNNER
# =========================================================

import sys
import os

# ---------------------------------------------------------
# FIX PYTHON PATH FOR 'src' IMPORTS
# ---------------------------------------------------------
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../..")
    )
)

# ---------------------------------------------------------
# IMPORT DASHBOARD
# ---------------------------------------------------------
from src.dashboard.app import main as dashboard_main


# ---------------------------------------------------------
# MAIN SYSTEM ENTRY
# ---------------------------------------------------------

def main():
    """
    Start system directly from dashboard.
    Launch panel is completely bypassed.
    """
    dashboard_main()


# ---------------------------------------------------------
# RUN APPLICATION
# ---------------------------------------------------------

if __name__ == "__main__":
    main()
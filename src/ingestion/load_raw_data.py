import sys
import os
import fastf1
import pandas as pd
import matplotlib.pyplot as plt


# -------------------------------------------------
# Enable FastF1 cache
# -------------------------------------------------
fastf1.Cache.enable_cache("cache")


# -------------------------------------------------
# Load race session
# -------------------------------------------------
def load_race_session(year: int, gp: str, session_type: str = "R"):
    print(f"\nLoading session: {year} {gp} ({session_type})")
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    print("Session loaded successfully")
    return session


# -------------------------------------------------
# STEP 2.8 — Derive max laps from dataset
# -------------------------------------------------
def get_max_laps_from_dataset(
    year: int,
    gp: str,
    session_type: str = "R"
) -> int:
    """
    Load race session and return maximum lap number
    available in the dataset.
    """

    print(
        f"[INFO] Extracting max laps from dataset "
        f"({year} {gp}, session={session_type})"
    )

    session = fastf1.get_session(year, gp, session_type)
    session.load()

    laps = session.laps

    if laps.empty or "LapNumber" not in laps.columns:
        raise ValueError(
            "Lap data is empty or missing LapNumber column."
        )

    max_lap = int(laps["LapNumber"].max())

    print(f"[INFO] Max laps found in dataset: {max_lap}")

    return max_lap


# -------------------------------------------------
# Inspect raw session data
# -------------------------------------------------
def inspect_session_data(session):
    print("\n--- DRIVERS ---")
    print(session.drivers)

    print("\n--- LAPS DATA (HEAD) ---")
    laps = session.laps
    print(laps.head())

    print("\n--- LAPS COLUMNS ---")
    print(laps.columns)

    print("\n--- LAPS INFO ---")
    print(laps.info())

    print("\n--- WEATHER DATA (HEAD) ---")
    weather = session.weather_data
    print(weather.head())
    print(weather.columns)

    print("\n--- CIRCUIT INFO ---")
    circuit_info = session.get_circuit_info()
    print(circuit_info)

    return laps, weather, circuit_info


# -------------------------------------------------
# Raw data visualizations (Step 2.13)
# -------------------------------------------------
def visualize_raw_data_basic(laps, driver_code, year, gp_name):
    output_dir = "outputs/raw_visualizations"
    os.makedirs(output_dir, exist_ok=True)

    safe_gp_name = gp_name.replace(" ", "_")
    driver_laps = laps.pick_driver(driver_code)

    if driver_laps.empty:
        print(f"No data found for driver: {driver_code}")
        return

    lap_numbers = driver_laps["LapNumber"]
    lap_times = driver_laps["LapTime"].dt.total_seconds()

    pit_laps = driver_laps[
        driver_laps["PitInTime"].notna()
    ]["LapNumber"]

    # Plot 1: Lap Time vs Lap
    plt.figure(figsize=(10, 4))
    plt.plot(lap_numbers, lap_times, marker="o")

    for pit_lap in pit_laps:
        plt.axvline(pit_lap, linestyle="--", alpha=0.5)

    plt.xlabel("Lap Number")
    plt.ylabel("Lap Time (seconds)")
    plt.title(f"Lap Time vs Lap — {driver_code}")
    plt.grid(True)

    lap_time_path = os.path.join(
        output_dir,
        f"{year}_{safe_gp_name}_{driver_code}_lap_time.png"
    )
    plt.savefig(lap_time_path)
    plt.show()
    plt.close()

    # Plot 2: Position vs Lap
    plt.figure(figsize=(10, 4))
    plt.plot(lap_numbers, driver_laps["Position"], marker="o")
    plt.gca().invert_yaxis()
    plt.xlabel("Lap Number")
    plt.ylabel("Position")
    plt.title(f"Position vs Lap — {driver_code}")
    plt.grid(True)

    position_path = os.path.join(
        output_dir,
        f"{year}_{safe_gp_name}_{driver_code}_position_vs_lap.png"
    )
    plt.savefig(position_path)
    plt.show()
    plt.close()

    # Plot 3: Lap Time Distribution
    plt.figure(figsize=(8, 4))
    plt.hist(lap_times.dropna(), bins=20)
    plt.xlabel("Lap Time (seconds)")
    plt.ylabel("Frequency")
    plt.title(f"Lap Time Distribution — {driver_code}")
    plt.grid(True)

    hist_path = os.path.join(
        output_dir,
        f"{year}_{safe_gp_name}_{driver_code}_lap_time_distribution.png"
    )
    plt.savefig(hist_path)
    plt.show()
    plt.close()

    print("\nPlots saved in:")
    print(os.path.abspath(output_dir))

    print("\nTyre usage (first 15 laps):")
    print(
        driver_laps[["LapNumber", "Compound", "TyreLife"]]
        .head(15)
    )


# -------------------------------------------------
# Main execution (standalone usage)
# -------------------------------------------------
if __name__ == "__main__":

    print("=== Formula 1 Raw Data Loader ===")

    try:
        year = int(input("Enter season year (e.g. 2023): ").strip())
    except ValueError:
        print("Invalid year entered. Exiting.")
        sys.exit(0)

    try:
        schedule = fastf1.get_event_schedule(year)
    except Exception as e:
        print(f"Failed to load schedule for {year}.")
        print(e)
        sys.exit(0)

    races = schedule[schedule["EventFormat"] == "conventional"]

    if races.empty:
        print(f"No race data available for year {year}.")
        sys.exit(0)

    available_gps = races["EventName"].tolist()

    print(f"\nAvailable Grands Prix in {year}:")
    for idx, gp in enumerate(available_gps, start=1):
        print(f"{idx}. {gp}")

    while True:
        choice = input(
            "\nSelect a Grand Prix by number (or type 'q' to quit): "
        ).strip()

        if choice.lower() == "q":
            sys.exit(0)

        if not choice.isdigit():
            print("Invalid input. Try again.")
            continue

        choice = int(choice)
        if choice < 1 or choice > len(available_gps):
            print("Invalid GP selection. Try again.")
            continue

        selected_gp = available_gps[choice - 1]
        break

    session = load_race_session(year, selected_gp, "R")
    laps, weather, circuit_info = inspect_session_data(session)

    available_drivers = sorted(laps["Driver"].unique().tolist())

    print("\nAvailable drivers in this race:")
    for idx, drv in enumerate(available_drivers, start=1):
        print(f"{idx}. {drv}")

    while True:
        drv_choice = input(
            "\nSelect a driver by number (or type 'q' to quit): "
        ).strip()

        if drv_choice.lower() == "q":
            sys.exit(0)

        if not drv_choice.isdigit():
            print("Invalid input. Try again.")
            continue

        drv_choice = int(drv_choice)
        if drv_choice < 1 or drv_choice > len(available_drivers):
            print("Invalid driver selection. Try again.")
            continue

        selected_driver = available_drivers[drv_choice - 1]
        break

    visualize_raw_data_basic(laps, selected_driver, year, selected_gp)

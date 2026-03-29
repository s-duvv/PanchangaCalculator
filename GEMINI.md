# Panchanga Project Overview

This project is a Hindu Panchanga (calendar) calculator implemented in Python. It calculates the five limbs (*Panchanga*) of the Hindu calendar—**Tithi**, **Vara**, **Nakshatra**, **Yoga**, and **Karana**—along with other essential elements like **Masa** (month), **Samvatsara** (year), **Ritu** (season), and **Ayana**.

The calculations are based on the **Swiss Ephemeris** (via the `pyswisseph` library) and follow the **Telugu/South-Indian (Amanta)** tradition with **Sidereal Lahiri** ayanamsha.

## Project Structure

- `PanchangaToday.py`: The main entry point. It calculates and prints the Panchanga for the current date and time at a configured location.
- `Tithi.py`: Calculates the lunar day (Tithi) based on the elongation between the Sun and the Moon.
- `Nakshatram.py`: Calculates the lunar mansion (Nakshatra) and the specific *pada* (quarter).
- `Vara.py`: Maps the weekday to its corresponding Sanskrit name.
- `Yoga.py`: Calculates the Yoga based on the sum of solar and lunar longitudes.
- `Karana.py`: Calculates the Karana (half-tithi).
- `Masa.py`: Calculates the lunar month (Masa), including logic for **Adhika** (intercalary) and **Nija** (regular) months.
- `Samvatsara.py`: Determines the name of the year in the 60-year Jovian cycle, anchored to the **Ugadi** (Lunar New Year).
- `Ayana.py`: Determines the solar half-year (**Uttarayana** or **Dakshinayana**).
- `Ritu.py`: Maps the lunar month to the corresponding season (**Ritu**).
- `ephe/`: Contains the Swiss Ephemeris data files (`.se1`) required for astronomical calculations.

## Building and Running

### Prerequisites

- **Python 3.x**
- **pyswisseph**: Python wrapper for the Swiss Ephemeris.
- **pytz**: World timezone definitions.

You can install the dependencies via pip:
```bash
pip install pyswisseph pytz
```

### Configuration

Before running, ensure the following in `PanchangaToday.py`:
1.  **Timezone**: Update the `tz` variable to your local timezone (e.g., `"Asia/Kolkata"` or `"US/Central"`).
2.  **Ephemeris Path**: The `EPHE_PATH` is set to the `ephe/` directory in the current working directory. Ensure this directory contains the necessary `.se1` files.

### Execution

To get the Panchanga for the current date and time (using the default US/Central timezone):
```bash
python3 PanchangaToday.py
```

To get the Panchanga for a specific date, time, and timezone:
```bash
python3 PanchangaToday.py --date 2024-04-09 --time 12:00:00 --timezone "Asia/Kolkata"
```

**Available Arguments:**
- `--date`: Date in `YYYY-MM-DD` format (defaults to today).
- `--time`: Time in `HH:MM:SS` format (defaults to now).
- `--timezone`: Timezone name (e.g., `"US/Central"`, `"Asia/Kolkata"`). Defaults to `"US/Central"`.

### Intuitive Interfaces (Front-ends)

We've added two more intuitive ways to run the Panchanga:

1. **Interactive CLI**:
   This will prompt you for date, time, and timezone using an interactive menu.
   ```bash
   python3 PanchangaInteractive.py
   ```

2. **Web Interface (Streamlit)**:
   A full-featured web dashboard to calculate and visualize the Panchanga.
   ```bash
   streamlit run PanchangaWeb.py
   ```

## Development Conventions

- **Ayanamsha**: The project strictly uses **Sidereal Lahiri** (`swe.SIDM_LAHIRI`).
- **Tradition**: It follows the **Amanta** system (month ends on Amavasya), common in South India (Andhra Pradesh, Telangana, Karnataka, Maharashtra).
- **Modularity**: Each component of the Panchanga is isolated in its own module for clarity and reusability.
- **Precision**: Uses bisection methods for finding exact conjunctions (new moons) to determine month and year boundaries.

## Key Files Summary

| File | Responsibility |
| :--- | :--- |
| `PanchangaToday.py` | Orchestrates all modules to print the daily Panchanga. |
| `Tithi.py` | Lunar day calculation (1-30). |
| `Nakshatram.py` | Moon's position in 27 Nakshatras. |
| `Masa.py` | Month calculation with Adhika/Nija logic. |
| `Samvatsara.py` | 60-year cycle name based on Ugadi. |
| `ephe/` | Binary ephemeris data (Swiss Ephemeris). |

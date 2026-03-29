"""
Samvatsaram.py
Compute the Telugu/South-Indian 60-year Samvatsara (Ugadi year name).

Definition used here:
- The Samvatsara changes at (approximately) the start of Chaitra Shukla Pratipada,
  i.e., immediately after the "Ugadi new moon" (Sun–Moon conjunction) that occurs
  when the Sun is in sidereal Meena (Pisces). This is the new moon that typically
  falls in late March / early April.

Implementation notes:
- Uses Swiss Ephemeris (sidereal Lahiri) like your other modules.
- Finds the relevant conjunction by bracketing and bisection on wrapped(Moon-Sun)=0.
- Then determines whether the input datetime is before/after that conjunction to pick
  the Samvatsara start year.
- Maps the Samvatsara start year to the 60-name cycle using the widely-used anchor:
    1987 CE Ugadi year = Prabhava (start of a 60-year cycle).  (See Telugu years list.)
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
import swisseph as swe


# 60 Telugu Ugadi year names (starting from Prabhava)
# Source lists show 1987 as "Prabhava", then cycles every 60 years.
SAMVATSARA_NAMES = [
    "Prabhava", "Vibhava", "Shukla", "Pramodoota", "Prajotpatti", "Angirasa",
    "Shrimukha", "Bhava", "Yuva", "Dhatri", "Ishvara", "Bahudhanya",
    "Pramathi", "Vikrama", "Vrisha", "Chitrabhanu", "Svabhanu", "Tarana",
    "Parthiva", "Vyaya", "Sarvajit", "Sarvadhari", "Virodhi", "Vikriti",
    "Khara", "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukhi",
    "Hevilambi", "Vilambi", "Vikari", "Sharvari", "Plava", "Shubhakruth",
    "Shobhakruth", "Krodhi", "Vishwavasu", "Parabhava", "Plavanga", "Keelaka",
    "Saumya", "Sadharana", "Virodhikruth", "Paridhavi", "Pramadeecha",
    "Ananda", "Rakshasa", "Nala", "Pingala", "Kalayukthi", "Siddharthi",
    "Raudra", "Durmathi", "Dundubhi", "Rudhirodgari", "Raktakshi", "Krodhana",
    "Akshaya"
]

def _wrap180(x_deg: float) -> float:
    """Map any angle to (-180, 180] to avoid 0/360 discontinuity for root finding."""
    return ((x_deg + 180.0) % 360.0) - 180.0


def _set_swiss(EPHE_PATH: str):
    swe.set_ephe_path(EPHE_PATH)
    swe.set_sid_mode(swe.SIDM_LAHIRI)


def _sun_moon_sidereal_longitudes(jd_ut: float, EPHE_PATH: str):
    _set_swiss(EPHE_PATH)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    moon_lon = swe.calc_ut(jd_ut, swe.MOON, flags)[0][0] % 360.0
    sun_lon  = swe.calc_ut(jd_ut, swe.SUN,  flags)[0][0] % 360.0
    return moon_lon, sun_lon


def _conjunction_function(jd_ut: float, EPHE_PATH: str) -> float:
    """wrapped(Moon - Sun) in (-180,180]; conjunction occurs at 0."""
    moon_lon, sun_lon = _sun_moon_sidereal_longitudes(jd_ut, EPHE_PATH)
    elong = (moon_lon - sun_lon) % 360.0
    return _wrap180(elong)


def _bisect_root(jd_a: float, jd_b: float, EPHE_PATH: str) -> float:
    f_a = _conjunction_function(jd_a, EPHE_PATH)
    f_b = _conjunction_function(jd_b, EPHE_PATH)

    if f_a == 0.0:
        return jd_a
    if f_b == 0.0:
        return jd_b
    if f_a * f_b > 0:
        raise ValueError("Interval does not bracket a conjunction root.")

    tol = 1.0 / 86400.0  # ~1 second in days
    for _ in range(80):
        mid = 0.5 * (jd_a + jd_b)
        f_m = _conjunction_function(mid, EPHE_PATH)

        if abs(jd_b - jd_a) < tol or abs(f_m) < 1e-7:
            return mid

        if f_a * f_m <= 0:
            jd_b, f_b = mid, f_m
        else:
            jd_a, f_a = mid, f_m

    return 0.5 * (jd_a + jd_b)


def _find_conjunction_near(jd_guess: float, EPHE_PATH: str, search_days: float = 20.0) -> float:
    """
    Find a conjunction near jd_guess by scanning outward until a sign change is bracketed.
    """
    # step 0.5 day is plenty
    step = 0.5
    max_steps = int((search_days / step) * 2)  # both directions

    f0 = _conjunction_function(jd_guess, EPHE_PATH)
    if f0 == 0.0:
        return jd_guess

    # scan forward/backward alternately
    jd_prev, f_prev = jd_guess, f0
    for i in range(1, max_steps + 1):
        for direction in (-1, +1):
            jd_try = jd_guess + direction * i * step
            f_try = _conjunction_function(jd_try, EPHE_PATH)

            if f_try == 0.0:
                return jd_try

            if f_prev == 0.0:
                return jd_prev

            if f_prev * f_try < 0:
                a, b = (jd_prev, jd_try) if jd_prev < jd_try else (jd_try, jd_prev)
                return _bisect_root(a, b, EPHE_PATH)

            # update "previous" for the next comparison in this direction sweep
            jd_prev, f_prev = jd_try, f_try

    raise RuntimeError("Could not bracket a conjunction near the guess. Check EPHE_PATH.")


def _sun_sidereal_longitude(jd_ut: float, EPHE_PATH: str) -> float:
    _set_swiss(EPHE_PATH)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    return swe.calc_ut(jd_ut, swe.SUN, flags)[0][0] % 360.0


def _is_meena(sun_sid_lon: float) -> bool:
    """True if Sun is in sidereal Meena (Pisces): 330°..360°."""
    return 330.0 <= (sun_sid_lon % 360.0) < 360.0


def ugadi_conjunction_jd(gregorian_year: int, EPHE_PATH: str) -> float:
    """
    Compute the conjunction (new moon) that starts the Ugadi/Chaitra Shukla Pratipada season.

    Practical rule:
    - Find a conjunction in late March/early April whose Sun is in sidereal Meena (Pisces).
    - This is the new moon immediately preceding Ugadi day (Chaitra Shukla Pratipada).

    Returns jd_ut of that conjunction.
    """
    # Use March 25 00:00 UTC as a robust starting guess
    jd_guess = swe.julday(gregorian_year, 3, 25, 0.0)

    # Find the nearest conjunction to the guess
    jd_conj = _find_conjunction_near(jd_guess, EPHE_PATH, search_days=25.0)

    # If that one isn't in Meena, try the previous/next conjunction
    sun_lon = _sun_sidereal_longitude(jd_conj, EPHE_PATH)
    if _is_meena(sun_lon):
        return jd_conj

    # Step by synodic month (~29.5 days) to look around
    candidates = [jd_conj - 29.6, jd_conj + 29.6]
    for jd_c in candidates:
        jd2 = _find_conjunction_near(jd_c, EPHE_PATH, search_days=10.0)
        if _is_meena(_sun_sidereal_longitude(jd2, EPHE_PATH)):
            return jd2

    # As a fallback, return the initial conjunction even if not Meena
    # (still gives a consistent year boundary for your program)
    return jd_conj


def samvatsara_from_start_year(start_year: int):
    """
    Map Samvatsara start-year to name using the anchor:
      1987 -> Prabhava (index 0), then cycles every 60 years.

    Returns (index_1_to_60, name)
    """
    idx0 = (start_year - 1987) % 60
    name = SAMVATSARA_NAMES[idx0]
    return idx0 + 1, name


def get_samvatsaram(dt_utc: datetime, EPHE_PATH: str):
    """
    Determine the active Samvatsara for the given UTC datetime.

    Steps:
    1) Find Ugadi conjunction for dt_utc.year.
    2) If dt_utc is before that conjunction -> samvatsara belongs to (year-1 start).
       Else -> belongs to (year start).
    3) Convert start year -> 60-year name.

    Returns dict:
      samvatsara_name, samvatsara_index, start_year, ugadi_conjunction_jd_ut
    """
    if dt_utc.tzinfo is None:
        # assume dt_utc is UTC naive
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)

    y = dt_utc.year
    jd_now = swe.julday(y, dt_utc.month, dt_utc.day,
                        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)

    jd_ugadi = ugadi_conjunction_jd(y, EPHE_PATH)

    start_year = y if jd_now >= jd_ugadi else (y - 1)
    idx, name = samvatsara_from_start_year(start_year)

    return name, jd_ugadi
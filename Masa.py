import math
from datetime import datetime
import swisseph as swe

RASHI_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka",
    "Simha", "Kanya", "Tula", "Vrischika",
    "Dhanu", "Makara", "Kumbha", "Meena"
]

# Month name = Sun's sidereal rashi at the Amavasya (new moon / conjunction)
MASA_FROM_RASHI = {
    # Telugu Amanta chandramana months (Chaitra..Phalguna) are conventionally
    # aligned so that "Chaitra" corresponds to the solar sidereal sign Meena (Pisces),
    # and the names advance with the Sun's sidereal rashi at the new moon.
    # This matches common Telugu calendars where Pushya/Pausha spans Dec–Jan, etc.
    "Meena": "Chaitra",
    "Mesha": "Vaishakha",
    "Vrishabha": "Jyeshtha",
    "Mithuna": "Ashadha",
    "Karka": "Shravana",
    "Simha": "Bhadrapada",
    "Kanya": "Ashwayuja",
    "Tula": "Kartika",
    "Vrischika": "Margashirsha",
    "Dhanu": "Pushya",
    "Makara": "Magha",
    "Kumbha": "Phalguna",
}

def _wrap180(x_deg: float) -> float:
    """Map any angle to (-180, 180]. Useful for root-finding without 0/360 discontinuity."""
    return ((x_deg + 180.0) % 360.0) - 180.0

def _set_swiss(EPHE_PATH: str):
    swe.set_ephe_path(EPHE_PATH)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

def _sun_moon_sidereal_longitudes(jd_ut: float, EPHE_PATH: str):
    """Return (moon_lon, sun_lon) in sidereal degrees [0, 360).

    Tries Swiss Ephemeris files first (SWIEPH). If ephemeris files are not available,
    falls back to the built-in Moshier ephemeris (MOSEPH).
    """
    _set_swiss(EPHE_PATH)

    def _calc(body):
        # Try SWIEPH first, then MOSEPH
        for base in (swe.FLG_SWIEPH, swe.FLG_MOSEPH):
            try:
                flags = base | swe.FLG_SIDEREAL
                return swe.calc_ut(jd_ut, body, flags)[0][0] % 360.0
            except swe.Error:
                continue
        raise

    moon_lon = _calc(swe.MOON)
    sun_lon  = _calc(swe.SUN)
    return moon_lon, sun_lon

def _conjunction_function(jd_ut: float, EPHE_PATH: str, return_raw: bool = False):
    """
    Signed Sun–Moon elongation near conjunction.

    Returns:
      f = wrap180( (Moon - Sun) mod 360 )  in (-180, 180]
    where conjunction (new moon) is at f = 0.

    If return_raw=True, also returns the raw elongation in [0, 360).
    """
    moon_lon, sun_lon = _sun_moon_sidereal_longitudes(jd_ut, EPHE_PATH)
    raw = (moon_lon - sun_lon) % 360.0
    f = _wrap180(raw)
    return (f, raw) if return_raw else f

def _find_conjunction(jd_start: float, EPHE_PATH: str, direction: int):
    """
    Find the nearest Sun–Moon conjunction (new moon) in the given direction.

    IMPORTANT: We only want conjunctions (elongation ~ 0°), not oppositions (~180°).
    A naive root-find on a wrapped angle can accidentally lock onto the ±180° discontinuity.
    This implementation brackets ONLY around the 0°/360° wrap by requiring samples to be
    "near conjunction" before accepting a sign-change bracket.

    direction: -1 for previous new moon, +1 for next new moon
    """
    if direction not in (-1, 1):
        raise ValueError("direction must be -1 (previous) or +1 (next)")

    # Step in 0.5-day increments; conjunctions occur about every 29.5 days.
    step = 0.5 * direction
    max_steps = 200  # 100 days window (very safe)

    jd_a = jd_start
    f_a, raw_a = _conjunction_function(jd_a, EPHE_PATH, return_raw=True)

    for _ in range(max_steps):
        jd_b = jd_a + step
        f_b, raw_b = _conjunction_function(jd_b, EPHE_PATH, return_raw=True)

        # "Near conjunction" if raw elongation is close to 0/360
        near_a = (raw_a < 60.0) or (raw_a > 300.0)
        near_b = (raw_b < 60.0) or (raw_b > 300.0)

        # If we hit essentially exact conjunction
        if near_a and abs(f_a) < 1e-6:
            return jd_a
        if near_b and abs(f_b) < 1e-6:
            return jd_b

        # Accept a bracket ONLY if BOTH endpoints are near conjunction
        # and the signed difference crosses 0.
        if near_a and near_b and (f_a == 0.0 or f_b == 0.0 or (f_a > 0 and f_b < 0) or (f_a < 0 and f_b > 0)):
            lo, hi = (jd_a, jd_b) if jd_a < jd_b else (jd_b, jd_a)
            return _bisect_conjunction(lo, hi, EPHE_PATH)

        jd_a, f_a, raw_a = jd_b, f_b, raw_b

    raise RuntimeError("Failed to locate a new moon conjunction within the search window. Check EPHE_PATH and time inputs.")

def _bisect_conjunction(jd_a: float, jd_b: float, EPHE_PATH: str):
    """Bisection refine root of conjunction function on [jd_a, jd_b]."""
    f_a = _conjunction_function(jd_a, EPHE_PATH)
    f_b = _conjunction_function(jd_b, EPHE_PATH)

    # Ensure it is bracketed
    if f_a == 0.0:
        return jd_a
    if f_b == 0.0:
        return jd_b
    if f_a * f_b > 0:
        raise ValueError("Interval does not bracket a root.")

    # Refine to ~1 second accuracy in JD (~1/86400 day)
    tol = 1.0 / 86400.0
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

def _rashi_from_lon(lon_sid_deg: float) -> str:
    """Sidereal rashi name from longitude."""
    idx = int(lon_sid_deg // 30.0) % 12
    return RASHI_NAMES[idx]

def _sun_rashi_at_jd(jd_ut: float, EPHE_PATH: str) -> str:
    """Sun sidereal rashi at given JD."""
    _set_swiss(EPHE_PATH)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_lon = swe.calc_ut(jd_ut, swe.SUN, flags)[0][0] % 360.0
    return _rashi_from_lon(sun_lon)

def get_masam(dt_utc: datetime, EPHE_PATH: str):
    """
    Compute the (Amanta) lunar month for the given UTC datetime, including Adhika Māsa detection.

    How Adhika Māsa is detected:
      Let A = most recent new moon (conjunction) before dt_utc
          B = next new moon after A
          P = new moon before A
      Let rA = Sun's sidereal rashi at A, rB at B, rP at P.
      Month name = MASA_FROM_RASHI[rA].

      - If rA == rB: the current month (A->B) is ADHIKA (leap) of that month name.
      - Else if rP == rA: the current month (A->B) is NIJA (regular) for that same month name
        (because the previous month (P->A) was the adhika one).
      - Else: normal month (no adhika/nija label needed).

    Returns a dict with:
      masa_name, masa_type ("ADHIKA" | "NIJA" | "NORMAL"),
      sun_rashi_at_newmoon, newmoon_jd_ut
    """
    _set_swiss(EPHE_PATH)
    jd_now = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)

    A = _find_conjunction(jd_now, EPHE_PATH, direction=-1)  # most recent new moon
    B = _find_conjunction(A + 1e-3, EPHE_PATH, direction=+1) # next new moon
    P = _find_conjunction(A - 1e-3, EPHE_PATH, direction=-1) # previous new moon

    rA = _sun_rashi_at_jd(A, EPHE_PATH)
    rB = _sun_rashi_at_jd(B, EPHE_PATH)
    rP = _sun_rashi_at_jd(P, EPHE_PATH)

    masa = MASA_FROM_RASHI[rA]

    if rA == rB:
        masa_type = "ADHIKA"
    elif rP == rA:
        masa_type = "NIJA"
    else:
        masa_type = "NORMAL"

    return masa, masa_type
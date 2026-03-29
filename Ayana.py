# Ayanam.py
# Determines Uttarayana / Dakshinayana using sidereal Sun longitude

import swisseph as swe

def get_sun_sidereal_longitude(year, month, day, hour_utc, EPHE_PATH):
    swe.set_ephe_path(EPHE_PATH)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    jd = swe.julday(year, month, day, hour_utc)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    lon = swe.calc_ut(jd, swe.SUN, flags)[0][0] % 360.0
    return lon

def get_ayanam(year, month, day, hour_utc, EPHE_PATH):
    """
    Returns:
      ("Uttarayana" or "Dakshinayana", sun_sidereal_longitude)
    """
    sun_lon = get_sun_sidereal_longitude(year, month, day, hour_utc, EPHE_PATH)

    if 90.0 <= sun_lon < 270.0:
        ayanam = "Dakshin"
    else:
        ayanam = "Uttar"
    return ayanam

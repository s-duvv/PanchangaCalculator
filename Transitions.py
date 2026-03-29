import math
import swisseph as swe
from datetime import datetime, timedelta
import pytz

# Constants for degree spans
TITHI_DEGREE = 12.0
NAKSHATRA_DEGREE = 360.0 / 27.0
YOGA_DEGREE = 360.0 / 27.0
KARANA_DEGREE = 6.0

def _set_swiss(ephe_path):
    swe.set_ephe_path(ephe_path)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

def _get_longitudes(jd_ut):
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_pos = swe.calc_ut(jd_ut, swe.SUN, flags)
    moon_pos = swe.calc_ut(jd_ut, swe.MOON, flags)
    return moon_pos[0][0] % 360.0, sun_pos[0][0] % 360.0

def _get_tithi_val(jd_ut):
    moon_lon, sun_lon = _get_longitudes(jd_ut)
    return (moon_lon - sun_lon) % 360.0

def _get_nakshatra_val(jd_ut):
    moon_lon, _ = _get_longitudes(jd_ut)
    return moon_lon % 360.0

def _get_yoga_val(jd_ut):
    moon_lon, sun_lon = _get_longitudes(jd_ut)
    return (moon_lon + sun_lon) % 360.0

def _get_karana_val(jd_ut):
    # Same as tithi but we track 6-degree intervals
    return _get_tithi_val(jd_ut)

def _bisect(func, jd_start, jd_end, target_val, degree_step, tol=1.0/86400.0):
    """
    Find jd in [jd_start, jd_end] such that func(jd) crosses target_val.
    Handles the 360/0 wrap.
    """
    # Normalize values relative to target_val
    def normalized_func(jd):
        val = func(jd)
        diff = (val - target_val) % 360.0
        if diff > 180: diff -= 360
        return diff

    f_start = normalized_func(jd_start)
    f_end = normalized_func(jd_end)

    # If it doesn't cross, something is wrong with the bracket
    if f_start * f_end > 0:
        # Not a strict bracket, but we can try to return the end if it's very close
        return jd_end

    for _ in range(20): # ~1 second precision
        mid = (jd_start + jd_end) / 2.0
        f_mid = normalized_func(mid)
        if abs(jd_end - jd_start) < tol:
            return mid
        if f_start * f_mid <= 0:
            jd_end = mid
            f_end = f_mid
        else:
            jd_start = mid
            f_start = f_mid
    return (jd_start + jd_end) / 2.0

def get_transitions_for_day(date_obj, tz_name, ephe_path):
    _set_swiss(ephe_path)
    tz = pytz.timezone(tz_name)
    
    # Start and end of the day in UTC
    dt_start = tz.localize(datetime.combine(date_obj, datetime.min.time()))
    dt_end = dt_start + timedelta(days=1)
    
    dt_start_utc = dt_start.astimezone(pytz.utc)
    jd_start = swe.julday(dt_start_utc.year, dt_start_utc.month, dt_start_utc.day, 
                          dt_start_utc.hour + dt_start_utc.minute/60.0 + dt_start_utc.second/3600.0)
    jd_end = jd_start + 1.0
    
    transitions = []
    
    # We'll check every hour to find brackets for transitions
    # This is safe since Tithi/Nakshatra/Yoga/Karana don't change twice in an hour (usually)
    # Actually Karana changes every ~12 hours, Tithi every ~24, Nakshatra ~24, Yoga ~24.
    # So hourly is very safe.
    
    steps = 24 * 4 # Every 15 minutes to be very safe for Karana
    step_size = 1.0 / steps
    
    for i in range(steps):
        t1 = jd_start + i * step_size
        t2 = jd_start + (i + 1) * step_size
        
        # Check Tithi
        v1 = _get_tithi_val(t1)
        v2 = _get_tithi_val(t2)
        idx1 = int(v1 // TITHI_DEGREE)
        idx2 = int(v2 // TITHI_DEGREE)
        if idx1 != idx2:
            target = (idx2 * TITHI_DEGREE) % 360.0
            jd_trans = _bisect(_get_tithi_val, t1, t2, target, TITHI_DEGREE)
            transitions.append(('Tithi', jd_trans, idx2 + 1))
            
        # Check Nakshatra
        v1 = _get_nakshatra_val(t1)
        v2 = _get_nakshatra_val(t2)
        idx1 = int(v1 // NAKSHATRA_DEGREE)
        idx2 = int(v2 // NAKSHATRA_DEGREE)
        if idx1 != idx2:
            target = (idx2 * NAKSHATRA_DEGREE) % 360.0
            jd_trans = _bisect(_get_nakshatra_val, t1, t2, target, NAKSHATRA_DEGREE)
            transitions.append(('Nakshatra', jd_trans, idx2 + 1))
            
        # Check Yoga
        v1 = _get_yoga_val(t1)
        v2 = _get_yoga_val(t2)
        idx1 = int(v1 // YOGA_DEGREE)
        idx2 = int(v2 // YOGA_DEGREE)
        if idx1 != idx2:
            target = (idx2 * YOGA_DEGREE) % 360.0
            jd_trans = _bisect(_get_yoga_val, t1, t2, target, YOGA_DEGREE)
            transitions.append(('Yoga', jd_trans, idx2 + 1))
            
        # Check Karana
        v1 = _get_karana_val(t1)
        v2 = _get_karana_val(t2)
        idx1 = int(v1 // KARANA_DEGREE)
        idx2 = int(v2 // KARANA_DEGREE)
        if idx1 != idx2:
            target = (idx2 * KARANA_DEGREE) % 360.0
            jd_trans = _bisect(_get_karana_val, t1, t2, target, KARANA_DEGREE)
            transitions.append(('Karana', jd_trans, idx2 + 1))

    # Sort transitions by time
    transitions.sort(key=lambda x: x[1])
    
    # Convert JD to local time strings
    results = []
    for type, jd, idx in transitions:
        # Convert JD to UTC datetime
        y, m, d, h = swe.revjul(jd)
        hour = int(h)
        minute = int((h - hour) * 60)
        second = int(((h - hour) * 60 - minute) * 60)
        dt_utc = datetime(y, m, d, hour, minute, second, tzinfo=pytz.utc)
        dt_local = dt_utc.astimezone(tz)
        
        # Only include if it falls within the requested day in local time
        if dt_local.date() == date_obj:
            results.append({
                'type': type,
                'time': dt_local.strftime('%I:%M %p'),
                'index': idx,
                'timestamp': dt_local
            })
            
    return results

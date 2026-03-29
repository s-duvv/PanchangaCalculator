import math
import swisseph as swe 

# 27 Nakshatra names 
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

Nakshatra_degree = 360.0/27.0

Pada_degree = Nakshatra_degree/4.0

def get_nakshatra(lon: float):
    """
    Returns (nakshatra_index_1_to_27, nakshatra_name, pada_1_to_4)
    """
    # 0..26
    idx0 = int(math.floor(lon / Nakshatra_degree)) % 27
    nak_name = NAKSHATRA_NAMES[idx0]

    # Pada within that nakshatra
    within = lon - (idx0 * Nakshatra_degree)
    pada = int(math.floor(within / Pada_degree)) + 1
    
    if pada > 4:
        pada = 4

    return nak_name, pada
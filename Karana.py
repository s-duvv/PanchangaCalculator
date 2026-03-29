import math

#7 Moving Karanas that repeat in the cycle
MOVABLE_KARANAS = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti"
]

# Fixed karanas occur at specific half-tithis
FIXED_KARANAS = {
    0: "Kimstughna",   # very first half-karana of the month
    57: "Shakuni",     # 58th half-karana
    58: "Chatushpada", # 59th half-karana
    59: "Naga"         # 60th half-karana
}

def get_karana(moon_lon: float, sun_lon: float):
    """
    Compute Karana from the tithi angle: (Moon - Sun) mod 360.
    Each karana spans 6 degrees (half of 12° tithi).
    """
    # Elongation used for tithi
    tithi_angle = (moon_lon - sun_lon) % 360.0  # 0..360

    # 60 segments of 6° each
    k0 = int(math.floor(tithi_angle / 6.0))     # 0..59
    k_num = k0 + 1

    # Half within current tithi (1st half or 2nd half)
    half_in_tithi = 1 if (k0 % 2 == 0) else 2

    # Map to karana name:
    if k0 in FIXED_KARANAS:
        name = FIXED_KARANAS[k0]
    else:
        # From the 2nd half-karana onward, movable cycle repeats
        # k0=1 corresponds to "Bava"
        name = MOVABLE_KARANAS[(k0 - 1) % 7]

    return name, half_in_tithi

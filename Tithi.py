import swisseph as swe

Tithi_names = [
    "Prathama", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya",
]

def get_longitude(year, month, day, hour, EPHE_PATH):
    """
    Return sidereal longitude of the moon and the sun for any given time
    this will be use to calculate tithi
    """
    
    #basic setup
    swe.set_ephe_path(EPHE_PATH)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    #Convert to Julian Day
    
    jd_ut = swe.julday(year, month, day, hour)
    
    # Compute geocentric sidereal longitue of sun and moon
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_pos = swe.calc_ut(jd_ut, swe.SUN, flags)
    moon_pos = swe.calc_ut(jd_ut, swe.MOON, flags)
    
    sun_longitude = sun_pos[0][0]
    moon_longitude = moon_pos[0][0]
    
    return moon_longitude, sun_longitude

def get_tithi(moon_longitude, sun_longitude):
    """
    Calculate tithi based on the longitudes of the moon and the sun
    """
    # Calculate the difference in longitude
    diff = (moon_longitude - sun_longitude) % 360
    
    # Each tithi is 12 degrees
    tithi_number = int(diff // 12) + 1  # Tithis are numbered from 1 to 30
    
    return tithi_number


def tithi(tithi_num):
    #1-15 = Shukla Paksha, 16-30 = Krishna Paksha
    if 1 <= tithi_num <= 15:
        paksha = "Shukla Paksha"
        index = tithi_num - 1
    else: 
        paksha = "Krishna Paksha"
        index = tithi_num - 16

    base_name = Tithi_names[index]
    
    #Additional logic for Amavasya and Purnima
    if tithi_num == 15:
        tithi_name = "Purnima"
    elif tithi_num == 30:
        tithi_name = "Amavasya"
    else:
        tithi_name = base_name
    
    return paksha, tithi_name
import math
import swisseph as swe

YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarman", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti"
]

YOGA_SPAN_DEG = 360.0 / 27.0  

def get_yoga(sun_sid_lon: float, moon_sid_lon: float):
    """
    Yoga is based on sun_lon plus moon_lon mod 360, and split into 27 parts
    """
    s = (sun_sid_lon + moon_sid_lon) % 360.0
    idx0 = int(math.floor(s / YOGA_SPAN_DEG)) % 27
    return YOGA_NAMES[idx0]

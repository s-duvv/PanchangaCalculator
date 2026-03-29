from typing import Dict, Tuple

# Canonical transliteration keys expected from Masam.py (adjust aliases below if needed)
RITU_FROM_MASA: Dict[str, str] = {
    "Chaitra": "Vasanta",
    "Vaishakha": "Vasanta",

    "Jyeshtha": "Grishma",
    "Ashadha": "Grishma",

    "Shravana": "Varsha",
    "Bhadrapada": "Varsha",

    "Ashwayuja": "Sharad",   # Telugu usage
    "Ashwin": "Sharad",
    "Ashvina": "Sharad",
    "Kartika": "Sharad",

    "Margashirsha": "Hemanta",
    "Pushya": "Hemanta",     

    "Magha": "Shishira",
    "Phalguna": "Shishira",
}

def get_ritu_from_masa(masa_name: str) -> Tuple[str, str]:


    ritu = RITU_FROM_MASA[masa_name]
    return ritu

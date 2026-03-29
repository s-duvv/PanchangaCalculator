def vara (weekday: int) -> str:
    """just a simple dict to convert between weekday and vara names"""
    convert = {
        6: "Bhanu",
        0: "Indu",
        1: "Bhauma",
        2: "Saumya",
        3: "Brihaspati",
        4: "Bhrugu",
        5: "Sthira"
    }
    return convert[weekday]
    
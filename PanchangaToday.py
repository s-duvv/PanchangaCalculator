import argparse
from datetime import date, datetime
from Vara import vara
from Tithi import *
from Nakshatram import *
from Karana import *
from Yoga import *
from Masa import *
from Samvatsara import *
from Ayana import *
from Ritu import *
import pytz
import os

def main():
    parser = argparse.ArgumentParser(description="Calculate Hindu Panchanga for a given date and time.")
    parser.add_argument("--date", type=str, help="Date in YYYY-MM-DD format (default: today)")
    parser.add_argument("--time", type=str, help="Time in HH:MM:SS format (default: now)")
    parser.add_argument("--timezone", type=str, default="US/Central", help="Timezone (default: US/Central)")
    
    args = parser.parse_args()

    # Configure timezone
    try:
        tz = pytz.timezone(args.timezone)
    except pytz.UnknownTimeZoneError:
        print(f"Error: Unknown timezone '{args.timezone}'. Defaulting to US/Central.")
        tz = pytz.timezone("US/Central")

    # Determine date
    if args.date:
        try:
            input_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"Error: Invalid date format '{args.date}'. Expected YYYY-MM-DD. Using today.")
            input_date = date.today()
    else:
        input_date = date.today()

    # Determine time
    if args.time:
        try:
            input_time = datetime.strptime(args.time, "%H:%M:%S").time()
        except ValueError:
            print(f"Error: Invalid time format '{args.time}'. Expected HH:MM:SS. Using current time.")
            input_time = datetime.now().time()
    else:
        input_time = datetime.now().time()

    # Combine into a localized datetime
    dt_local = tz.localize(datetime.combine(input_date, input_time))
    dt_utc = dt_local.astimezone(pytz.utc)

    # Configuration for Ephemeris
    EPHE_PATH = os.path.join(os.getcwd(), "ephe")
    if not os.path.exists(EPHE_PATH):
        print(f"Warning: Ephemeris path {EPHE_PATH} not found.")

    # Time setup for Swiss Ephemeris
    year, month, day = dt_utc.year, dt_utc.month, dt_utc.day
    hour = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0

    # Panchanga Calculations
    moon_longitude, sun_longitude = get_longitude(year, month, day, hour, EPHE_PATH)
    tithi_num = get_tithi(moon_longitude, sun_longitude)
    paksha, tithi_name = tithi(tithi_num)
    
    nak_name, pada = get_nakshatra(moon_longitude)
    karana_name, karana_status = get_karana(moon_longitude, sun_longitude)
    yoga_name = get_yoga(moon_longitude, sun_longitude)
    masa_name, masa_type = get_masam(dt_utc, EPHE_PATH)
    samvatsara_name, ugadi = get_samvatsaram(dt_utc, EPHE_PATH)
    ayana_name = get_ayanam(year, month, day, hour, EPHE_PATH)
    ritu_name = get_ritu_from_masa(masa_name)

    # Vara is based on the input local date
    weekday_number = input_date.weekday()

    # Final Output
    print(f"\nPanchanga for {dt_local.strftime('%Y-%m-%d %H:%M:%S %Z')}:")
    print(f"Using ephemeris data from: {EPHE_PATH}")
    print(f"For Sandhya Vandanam Read: {samvatsara_name}-nama saṃvatsarē, {ayana_name} ayanē, {ritu_name} ṛtē, {masa_name} māsē, {paksha} pakṣē, {tithi_name} tithau, {vara(weekday_number)} vāsarē, {nak_name} nakṣatra, {yoga_name} yōga, {karana_name} karaṇa")

if __name__ == "__main__":
    main()

import questionary
from datetime import date, datetime
import pytz
import os
import subprocess
from Vara import vara
from Tithi import *
from Nakshatram import *
from Karana import *
from Yoga import *
from Masa import *
from Samvatsara import *
from Ayana import *
from Ritu import *

def main():
    print("\n--- 🕉️ Hindu Panchanga Interactive ---")
    
    # 1. Select Date
    use_today = questionary.confirm("Use today's date?", default=True).ask()
    if use_today:
        selected_date = date.today().strftime("%Y-%m-%d")
    else:
        selected_date = questionary.text(
            "Enter date (YYYY-MM-DD):",
            default=date.today().strftime("%Y-%m-%d"),
            validate=lambda val: True if len(val) == 10 and "-" in val else "Format must be YYYY-MM-DD"
        ).ask()

    # 2. Select Time
    use_now = questionary.confirm("Use current time?", default=True).ask()
    if use_now:
        selected_time = datetime.now().strftime("%H:%M:%S")
    else:
        selected_time = questionary.text(
            "Enter time (HH:MM:SS):",
            default=datetime.now().strftime("%H:%M:%S"),
            validate=lambda val: True if len(val) == 8 and ":" in val else "Format must be HH:MM:SS"
        ).ask()

    # 3. Select Timezone
    common_timezones = [
        "US/Central",
        "Asia/Kolkata",
        "US/Eastern",
        "US/Pacific",
        "Europe/London",
        "Asia/Singapore",
        "Asia/Dubai",
        "UTC"
    ]
    selected_timezone = questionary.select(
        "Select Timezone:",
        choices=common_timezones + ["Other (Type name)"]
    ).ask()

    if selected_timezone == "Other (Type name)":
        selected_timezone = questionary.text(
            "Enter IANA Timezone name (e.g., Europe/London):",
            validate=lambda val: True if val in pytz.all_timezones else "Invalid timezone"
        ).ask()

    # 4. Execute and show results
    print(f"\nCalculating Panchanga for {selected_date} {selected_time} ({selected_timezone})...")
    
    # We can either import and call the logic or run the subprocess
    # Let's import the logic to be cleaner, but we need to pass the arguments.
    # For simplicity, I'll just run the subprocess of PanchangaToday.py or just call main logic.
    
    try:
        # Reusing the logic from PanchangaToday.py
        tz = pytz.timezone(selected_timezone)
        input_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
        input_time = datetime.strptime(selected_time, "%H:%M:%S").time()
        
        dt_local = tz.localize(datetime.combine(input_date, input_time))
        dt_utc = dt_local.astimezone(pytz.utc)

        EPHE_PATH = os.path.join(os.getcwd(), "ephe")
        year, month, day = dt_utc.year, dt_utc.month, dt_utc.day
        hour = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0

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

        weekday_number = input_date.weekday()

        print("\n" + "="*60)
        print(f"RESULTS FOR {dt_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print("="*60)
        print(f"📅 Date & Time  : {dt_local.strftime('%A, %B %d, %Y %I:%M:%S %p')}")
        print(f"🌍 Timezone     : {selected_timezone}")
        print("-" * 60)
        print(f"🔱 Samvatsara    : {samvatsara_name}")
        print(f"☀️ Ayana         : {ayana_name}")
        print(f"🌿 Ritu          : {ritu_name}")
        print(f"🌙 Masa          : {masa_name}")
        print(f"🌗 Paksha        : {paksha}")
        print(f"📆 Tithi         : {tithi_name}")
        print(f"🌞 Vara          : {vara(weekday_number)}")
        print(f"✨ Nakshatram    : {nak_name}")
        print(f"⚛️ Yoga          : {yoga_name}")
        print(f"🐘 Karana        : {karana_name}")
        print("-" * 60)
        print(f"\n✨ For Sandhya Vandanam:")
        print(f"{samvatsara_name}-nama saṃvatsarē, {ayana_name} ayanē, {ritu_name} ṛtē, {masa_name} māsē, {paksha} pakṣē, {tithi_name} tithau, {vara(weekday_number)} vāsarē, {nak_name} nakṣatra, {yoga_name} yōga, {karana_name} karaṇa")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()

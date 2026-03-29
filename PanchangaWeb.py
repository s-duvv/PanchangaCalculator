import streamlit as st
from datetime import date, datetime
import pytz
import os
from Vara import vara
from Tithi import *
from Nakshatram import *
from Karana import *
from Yoga import *
from Masa import *
from Samvatsara import *
from Ayana import *
from Ritu import *

from Transitions import get_transitions_for_day

st.set_page_config(page_title="Hindu Panchanga", page_icon="🕉️", layout="wide")

st.title("🕉️ Hindu Panchanga Calculator")
st.markdown("Calculate the five limbs of the Hindu calendar (Tithi, Vara, Nakshatra, Yoga, Karana).")

# Sidebar for inputs
st.sidebar.header("Configuration")

selected_date = st.sidebar.date_input("Select Date", date.today())
selected_time = st.sidebar.time_input("Select Time", datetime.now().time())
selected_timezone = st.sidebar.selectbox("Select Timezone", pytz.all_timezones, index=pytz.all_timezones.index("US/Central") if "US/Central" in pytz.all_timezones else 0)

def get_karana_name(k0):
    # k0 is 0-59 index
    if k0 in FIXED_KARANAS:
        return FIXED_KARANAS[k0]
    else:
        return MOVABLE_KARANAS[(k0 - 1) % 7]

if st.sidebar.button("Calculate"):
    try:
        tz = pytz.timezone(selected_timezone)
        dt_local = tz.localize(datetime.combine(selected_date, selected_time))
        dt_utc = dt_local.astimezone(pytz.utc)

        EPHE_PATH = os.path.join(os.getcwd(), "ephe")
        
        # Progress bar
        with st.spinner('Calculating...'):
            # Current Moment Calculation
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

            weekday_number = selected_date.weekday()

            # Daily Transitions Calculation
            day_transitions = get_transitions_for_day(selected_date, selected_timezone, EPHE_PATH)
            
            # Get 12 AM state
            dt_12am_local = tz.localize(datetime.combine(selected_date, datetime.min.time()))
            dt_12am_utc = dt_12am_local.astimezone(pytz.utc)
            m12, s12 = get_longitude(dt_12am_utc.year, dt_12am_utc.month, dt_12am_utc.day, 
                                     dt_12am_utc.hour + dt_12am_utc.minute/60.0, EPHE_PATH)
            t12 = get_tithi(m12, s12)
            n12, _ = get_nakshatra(m12)
            y12 = get_yoga(m12, s12)
            k12, _ = get_karana(m12, s12)

        # Display Results
        st.success(f"Results for {dt_local.strftime('%A, %B %d, %Y %I:%M:%S %p %Z')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Samvatsara", samvatsara_name)
            st.metric("Ayana", ayana_name)
            st.metric("Ritu", ritu_name)
            st.metric("Masa", masa_name)
            st.metric("Paksha", paksha)

        with col2:
            st.metric("Tithi", tithi_name)
            st.metric("Vara", vara(weekday_number))
            st.metric("Nakshatram", nak_name)
            st.metric("Yoga", yoga_name)
            st.metric("Karana", karana_name)

        st.divider()
        
        # New Section: Daily Breakdown
        st.subheader("📅 Daily Timeline (12 AM - 11:59 PM)")
        st.write(f"Showing how the Panchanga limbs change throughout {selected_date.strftime('%B %d, %Y')}")
        
        # Initial State at 12 AM
        timeline_data = [
            {"Time": "12:00 AM", "Event": "Start of Day", "Details": f"Tithi: {tithi(t12)[1]}, Nakshatra: {n12}, Yoga: {y12}, Karana: {k12}"}
        ]
        
        for t in day_transitions:
            name = ""
            if t['type'] == 'Tithi':
                _, name = tithi(t['index'])
            elif t['type'] == 'Nakshatra':
                name = NAKSHATRA_NAMES[(t['index'] - 1) % 27]
            elif t['type'] == 'Yoga':
                name = YOGA_NAMES[(t['index'] - 1) % 27]
            elif t['type'] == 'Karana':
                name = get_karana_name(t['index'] - 1)
            
            timeline_data.append({
                "Time": t['time'],
                "Event": f"{t['type']} Change",
                "Details": f"Now {name}"
            })
            
        st.table(timeline_data)

        st.divider()
        st.subheader("✨ For Sandhya Vandanam")
        sandhya_text = f"{samvatsara_name}-nama saṃvatsarē, {ayana_name} ayanē, {ritu_name} ṛtē, {masa_name} māsē, {paksha} pakṣē, {tithi_name} tithau, {vara(weekday_number)} vāsarē, {nak_name} nakṣatra, {yoga_name} yōga, {karana_name} karaṇa"
        st.code(sandhya_text, language=None)
        
        st.info("Note: This calculation uses Sidereal Lahiri ayanamsha and Amanta tradition.")

    except Exception as e:
        st.error(f"Error during calculation: {e}")
else:
    st.info("Adjust the settings in the sidebar and click 'Calculate' to see the Panchanga.")

st.markdown("---")
st.caption("Powered by Swiss Ephemeris (pyswisseph)")

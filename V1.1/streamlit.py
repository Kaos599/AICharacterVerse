# streamlit_app.py
import streamlit as st
import json
import os
import random
import schedule
import time
import threading
from datetime import datetime
from character import CharacterSimulator
from data_handler import load_character_dna, save_character_dna, load_json, load_supporting_characters
from utils import format_datetime
from config import DNA_FILE, SUPPORTING_CHARS_DIR, RANDOM_EVENTS_FILE

st.title("AI Character Simulation")

if 'simulator' not in st.session_state:
    st.session_state['simulator'] = CharacterSimulator()

simulator = st.session_state['simulator']

st.sidebar.title("Character Actions")
if st.sidebar.button("Simulate Instagram Post"):
    simulator.simulate_instagram_post()
    st.experimental_rerun()

if st.sidebar.button("Simulate Twitter Post"):
    simulator.simulate_twitter_post()
    st.experimental_rerun()

if st.sidebar.button("Simulate WhatsApp Chat"):
    simulator.simulate_whatsapp_chat()
    st.experimental_rerun()

if st.sidebar.button("Simulate Daily Routine Event"):
    simulator.simulate_daily_routine()
    st.experimental_rerun()

st.sidebar.title("Admin Mode")
if st.sidebar.checkbox("Enable Edit DNA"):
    with st.sidebar.expander("Edit Main Character DNA"):
        dna_content = json.dumps(simulator.dna, indent=4)
        updated_dna_json = st.text_area("Edit DNA Content (JSON)", dna_content, height=300)
        if st.sidebar.button("Save DNA Changes"):
            try:
                updated_dna = json.loads(updated_dna_json)
                save_character_dna(DNA_FILE, updated_dna)
                simulator.dna = updated_dna
                st.success("DNA updated successfully. Please refresh the app.")
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON format: {e}")
            except Exception as e:
                st.error(f"Error updating DNA: {e}")

    with st.sidebar.expander("Add Supporting Character"):
        new_char_name = st.text_input("Character Name")
        if new_char_name:
            if st.sidebar.button(f"Create {new_char_name}"):
                default_char = {"name": new_char_name, "personality": "Friendly", "interests": [],"current_mood": "Neutral",
                                  "energy_level": 5, "social_battery": 5, "stress_level": 5}
                filepath = os.path.join(SUPPORTING_CHARS_DIR, f"{new_char_name.lower().replace(' ', '_')}.json")
                save_character_dna(filepath, default_char)
                simulator.supporting_characters = load_supporting_characters(SUPPORTING_CHARS_DIR)
                st.success(f"Supporting character '{new_char_name}' created.")
                st.experimental_rerun()

st.header("Social Media Feed")
platform = st.selectbox("Select Platform", ["Instagram", "Twitter", "WhatsApp", "Daily Events"])

if platform == "Instagram":
    st.subheader("Instagram")
    for post in reversed(simulator.instagram_history):
        timestamp_obj = datetime.fromisoformat(post['timestamp'])
        st.write(f"**{simulator.name}** - {format_datetime(timestamp_obj)}")
        if 'description' in post:
            st.write(f"Description: {post['description']}")
        st.write(post['content'])
        if "suggested_visual" in post.get('gemini_data', {}):
            st.image("https://placekitten.com/200/300", caption=post['gemini_data']['suggested_visual'])
        st.write(f"❤️ {post['likes']} Likes")
        for comment in post['comments']:
            st.write(f"> **{comment['author']}**: {comment['text']}")
        st.markdown("---")

elif platform == "Twitter":
    st.subheader("Twitter")
    for tweet in reversed(simulator.twitter_history):
        timestamp_obj = datetime.fromisoformat(tweet['timestamp'])
        st.write(f"**{simulator.name}** - {format_datetime(timestamp_obj)}")
        st.write(tweet['content'])
        st.markdown("---")

elif platform == "WhatsApp":
    st.subheader("WhatsApp")
    for message in simulator.whatsapp_history:
        sender = message['sender']
        text = message['message']
        timestamp_obj = datetime.fromisoformat(message['timestamp'])
        st.write(f"**{sender}**: {text}  *({format_datetime(timestamp_obj)} )*")

elif platform == "Daily Events":
    st.subheader("Daily Events")
    events_data = load_json(RANDOM_EVENTS_FILE)
    if isinstance(events_data, dict) and "log" in events_data:
        for event in reversed(events_data["log"]):
            timestamp_str = event.get('timestamp')
            if timestamp_str:
                timestamp_obj = datetime.fromisoformat(timestamp_str)
                st.write(f"{format_datetime(timestamp_obj)} - {event.get('name', event.get('event','No Name'))}")
            else:
                st.write(f"No Timestamp - {event.get('name', event.get('event','No Name'))}")
            if 'details' in event:
                st.write(f"Details: {event['details']}")
            if 'involved_characters' in event:
                st.write(f"Involved Characters: {', '.join(event['involved_characters'])}")
            st.markdown("---")

def daily_scheduled_tasks():
    simulator.run_daily_updates()

schedule.every().day.at("08:00").do(daily_scheduled_tasks)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

st.sidebar.text("Daily updates scheduled...")

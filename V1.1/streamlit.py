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
import uuid  # Import the uuid library

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

if st.sidebar.button("Simulate Supporting Character Post"):
    simulator.simulate_supporting_character_post()
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

    # Add the live updates checkbox in the sidebar
    auto_update = st.sidebar.checkbox("Enable Live Updates", value=True)

    for post in reversed(simulator.instagram_history):
        with st.container():
            # Create a clean card-like container
            st.markdown("""
            <style>
            .instagram-post {
                border: 1px solid #dbdbdb;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 20px;
                background-color: white;
            }
            </style>
            """, unsafe_allow_html=True)

            # Post container
            with st.container():
                # Header with profile picture and name/timestamp
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.image("https://placekitten.com/50/50", width=50)
                with col2:
                    timestamp_obj = datetime.fromisoformat(post['timestamp'])
                    st.write(f"**{post.get('author', simulator.name)}**")
                    st.write(f"*{format_datetime(timestamp_obj)}*")

                # Post image
                st.image("https://placekitten.com/600/400", use_column_width=True)

                # Post content (caption and visual description)
                if 'content' in post:
                    content = post['content']
                    caption_start = content.lower().find('caption:')
                    visual_start = content.lower().find('visual description:')

                    if caption_start != -1 and visual_start != -1:
                        caption = content[caption_start + 8:visual_start].strip()
                        visual_desc = content[visual_start + 18:].strip()

                        st.write(f"**Caption:** {caption}")
                        with st.expander("View Visual Description"):
                            st.write(visual_desc)

                # Likes and interaction buttons
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.write(f"❤️ {post['likes']} Likes")
                with col2:
                    if st.button("Like 👍", key=f"like_{post['timestamp']}"):
                        post['likes'] += 1
                        simulator._save_instagram_history()
                        st.experimental_rerun()

                # Comments section
                st.write("**Comments**")
                if 'comments' in post:
                    for comment in post.get('comments', []):
                        with st.container():
                            # Calculate indentation based on parent_id
                            indent = 0
                            if 'parent_id' in comment:
                                indent = 20  # pixels

                            st.markdown(f"""
                            <div style='margin-left: {indent}px; padding: 8px;
                                      margin-top: 4px; background-color: #f0f2f5;
                                      border-radius: 8px;'>
                                <strong>{comment['author']}</strong>: {comment['text']}
                            </div>
                            """, unsafe_allow_html=True)

                # Add comment form
                with st.form(key=f"comment_form_{post['timestamp']}"):
                    new_comment = st.text_input("Add a comment...", key=f"comment_input_{post['timestamp']}")
                    if st.form_submit_button("Post Comment"):
                        if new_comment:
                            if 'comments' not in post:
                                post['comments'] = []

                            # Create new comment
                            comment = {
                                'author': simulator.name,
                                'text': new_comment,
                                'timestamp': datetime.now().isoformat(),
                                'id': str(uuid.uuid4())
                            }

                            # If this is a reply to another comment
                            last_comment = post['comments'][-1] if post['comments'] else None
                            if last_comment:
                                comment['parent_id'] = last_comment.get('id')

                            post['comments'].append(comment)
                            simulator._save_instagram_history()
                            st.experimental_rerun()

                st.markdown("---")

    # Auto-update functionality
    if auto_update:
        simulator.update_post_interactions()
        time.sleep(5)
        st.experimental_rerun()

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
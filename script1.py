import streamlit as st
import json
import os
import random
from datetime import datetime
import schedule
import time
from typing import Dict, Any, List


try:
    import google.generativeai as genai
    
    genai.configure(api_key=os.environ.get("AIzaSyBEWgDXRyFMHJpXG9bHZZFyDDKDYVEWY2k"))
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 200,  
    }
    model = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config)
except ImportError:
    print("Warning: google-generativeai library not found. Content generation will be limited.")
    model = None

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

DNA_FILE = os.path.join(DATA_DIR, "dna_main.txt")
INSTAGRAM_HISTORY_FILE = os.path.join(DATA_DIR, "instagram_history.json")
TWITTER_HISTORY_FILE = os.path.join(DATA_DIR, "twitter_history.json")
WHATSAPP_HISTORY_FILE = os.path.join(DATA_DIR, "whatsapp_history.json")
RANDOM_EVENTS_FILE = os.path.join(DATA_DIR, "random_events.json")
SUPPORTING_CHARS_DIR = os.path.join(DATA_DIR, "supporting_characters")
os.makedirs(SUPPORTING_CHARS_DIR, exist_ok=True)

def load_dna(filepath: str) -> Dict[str, Any]:
    """Loads the character's DNA from a text file."""
    dna = {}
    current_section = None
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if ':' not in line and line.endswith(':'):
                current_section = line[:-1].strip()
                dna[current_section] = {}
            elif ':' in line and current_section:
                key, value = line.split(':', 1)
                dna[current_section][key.strip()] = value.strip()
    return dna

def save_json(filepath: str, data: Any):
    """Saves data to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_json(filepath: str) -> Any:
    """Loads data from a JSON file."""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return []

def load_supporting_characters() -> Dict[str, Dict[str, Any]]:
    """Loads all supporting characters from JSON files in the supporting_characters directory."""
    characters = {}
    for filename in os.listdir(SUPPORTING_CHARS_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(SUPPORTING_CHARS_DIR, filename)
            with open(filepath, 'r') as f:
                char_data = json.load(f)
                characters[char_data['name']] = char_data
    return characters

def generate_gemini_content(prompt: str) -> str:
    """Generates content using Google's Gemini AI."""
    if model:
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating content with Gemini: {e}")
            return ""
    else:
        return "Gemini API not available."

class CharacterSimulator:
    def __init__(self):
        self.dna = load_dna(DNA_FILE)
        self.instagram_history = load_json(INSTAGRAM_HISTORY_FILE)
        self.twitter_history = load_json(TWITTER_HISTORY_FILE)
        self.whatsapp_history = load_json(WHATSAPP_HISTORY_FILE)
        self.random_events = load_json(RANDOM_EVENTS_FILE)
        self.supporting_characters = load_supporting_characters()
        self.name = self.dna.get("Basic Information", {}).get("Name", "AI Character")

    def _get_random_supporting_character(self):
        if self.supporting_characters:
            return random.choice(list(self.supporting_characters.values()))
        return None

    def _generate_social_media_post(self, platform: str, prompt_prefix: str = ""):
        if model:
            prompt = f"{prompt_prefix} Generate a social media post for {self.name} on {platform} based on their personality and interests. "
            if platform == "Instagram":
                prompt += "Include a short caption and suggest a visual description."
            elif platform == "Twitter":
                prompt += "Keep it concise and reflect their typical tone."
            response_text = generate_gemini_content(prompt)
            return response_text
        else:
            return f"Simulated {platform} post from {self.name}: [No AI content generated]"

    def _generate_whatsapp_message(self, recipient_name: str, prompt_prefix: str = ""):
        if model:
            prompt = f"{prompt_prefix} Simulate a WhatsApp message from {self.name} to {recipient_name} based on their personalities and relationship."
            return generate_gemini_content(prompt)
        else:
            return f"{self.name}: [Simulated message to {recipient_name}]"

    def simulate_instagram_post(self):
        post_content = self._generate_social_media_post("Instagram")
        likes = random.randint(10, 300)
        comments = []
        num_comments = random.randint(0, 5)
        for _ in range(num_comments):
            commenter = self._get_random_supporting_character()
            if commenter:
                comment_prompt = f"Generate a short comment from {commenter['name']} on a post by {self.name}."
                comment_text = generate_gemini_content(comment_prompt) if model else "Nice post!"
                comments.append({"author": commenter['name'], "text": comment_text})

        post = {"timestamp": datetime.now().isoformat(), "content": post_content, "likes": likes, "comments": comments}
        self.instagram_history.append(post)
        save_json(INSTAGRAM_HISTORY_FILE, self.instagram_history)
        return post

    def simulate_twitter_post(self):
        post_content = self._generate_social_media_post("Twitter")
        post = {"timestamp": datetime.now().isoformat(), "content": post_content}
        self.twitter_history.append(post)
        save_json(TWITTER_HISTORY_FILE, self.twitter_history)
        return post

    def simulate_whatsapp_chat(self):
        recipient = self._get_random_supporting_character()
        if not recipient:
            return None

        message_to_recipient = self._generate_whatsapp_message(recipient['name'])
        self.whatsapp_history.append({
            "timestamp": datetime.now().isoformat(),
            "sender": self.name,
            "recipient": recipient['name'],
            "message": message_to_recipient
        })

        
        response_prompt = f"Simulate a WhatsApp response from {recipient['name']} to {self.name}'s message: '{message_to_recipient}'."
        response_message = generate_gemini_content(response_prompt) if model else "Okay."
        self.whatsapp_history.append({
            "timestamp": datetime.now().isoformat(),
            "sender": recipient['name'],
            "recipient": self.name,
            "message": response_message
        })

        save_json(WHATSAPP_HISTORY_FILE, self.whatsapp_history)
        return self.whatsapp_history[-2:] 

    def simulate_daily_routine(self):
        hour = datetime.now().hour
        event = None
        if 6 <= hour < 10:
            event = f"{self.name} is having {self.dna.get('Interests and Hobbies', {}).get('Favourite foods', 'breakfast')}."
        elif 10 <= hour < 18:
            event = f"{self.name} is at work as an {self.dna.get('Basic Information', {}).get('Career path', 'employee')}."
        elif 18 <= hour < 22:
            hobby = random.choice(self.dna.get("Interests and Hobbies", {}).get("Hobbies", ["relaxing"]))
            event = f"{self.name} is spending the evening {hobby}."
        else:
            event = f"{self.name} is likely sleeping."

        if event:
            self.random_events.append({"timestamp": datetime.now().isoformat(), "event": event})
            save_json(RANDOM_EVENTS_FILE, self.random_events)
            return event
        return None

    def run_daily_updates(self):
        
        if random.random() < 0.3:
            self.simulate_instagram_post()
        if random.random() < 0.2:
            self.simulate_twitter_post()
        if random.random() < 0.1:
            self.simulate_whatsapp_chat()
        self.simulate_daily_routine()


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
        with open(DNA_FILE, "r") as f:
            dna_content = f.read()
        updated_dna = st.text_area("Edit DNA Content", dna_content, height=300)
        if st.sidebar.button("Save DNA Changes"):
            try:
                
                load_dna(DNA_FILE) 
                with open(DNA_FILE, "w") as f:
                    f.write(updated_dna)
                st.success("DNA updated successfully. Please refresh the app.")
            except Exception as e:
                st.error(f"Error updating DNA: {e}")

    with st.sidebar.expander("Add Supporting Character"):
        new_char_name = st.text_input("Character Name")
        if new_char_name:
            if st.sidebar.button(f"Create {new_char_name}"):
                default_char = {"name": new_char_name, "personality": "Friendly", "interests": []}
                filepath = os.path.join(SUPPORTING_CHARS_DIR, f"{new_char_name.lower().replace(' ', '_')}.json")
                save_json(filepath, default_char)
                simulator.supporting_characters = load_supporting_characters()
                st.success(f"Supporting character '{new_char_name}' created.")
                st.experimental_rerun()

st.header("Social Media Feed")
platform = st.selectbox("Select Platform", ["Instagram", "Twitter", "WhatsApp", "Daily Events"])

if platform == "Instagram":
    st.subheader("Instagram")
    for post in reversed(simulator.instagram_history):
        st.write(f"**{simulator.name}** - {post['timestamp']}")
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
        st.write(f"**{simulator.name}** - {tweet['timestamp']}")
        st.write(tweet['content'])
        st.markdown("---")

elif platform == "WhatsApp":
    st.subheader("WhatsApp")
    for message in simulator.whatsapp_history:
        sender = message['sender']
        text = message['message']
        st.write(f"**{sender}**: {text}  *({message['timestamp']})*")

elif platform == "Daily Events":
    st.subheader("Daily Events")
    for event in reversed(simulator.random_events):
        st.write(f"{event['timestamp']} - {event['event']}")
        st.markdown("---")


def daily_scheduled_tasks():
    simulator.run_daily_updates()
    
    
    
    
    

schedule.every().day.at("08:00").do(daily_scheduled_tasks) 

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)  



import threading
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

st.sidebar.text("Daily updates scheduled...")
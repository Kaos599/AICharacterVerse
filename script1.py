import streamlit as st
import json
import os
import random
from datetime import datetime
import schedule
import time
from typing import Dict, Any, List
import threading

try:
    import google.generativeai as genai
    
    genai.configure(api_key=os.environ.get("AIzaSyBEWgDXRyFMHJpXG9bHZZFyDDKDYVEWY2k"))
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,  
    }
    model = genai.GenerativeModel(model_name="gemini-2.0-flash-thinking-exp-1219", generation_config=generation_config, system_instruction="""You are simulating the online presence of a fictional character.
    Here's how to interpret the character's traits to generate realistic content:
    
    **Basic Information**: Use this for factual details about the character.
    
    **Personality**:
      - **Positive characteristics**: Aspects to emphasize in positive contexts.
      - **Negative characteristics**:  Flaws that might surface in arguments or stressful situations.
      - **Words often used**: Incorporate these phrases naturally into their speech and posts.
      - **Other words that might be used**: Expand vocabulary with these related terms.
      - **Moral**: Dictates their sense of right and wrong. A lower moral score might mean they are more likely to be mischievous or unethical.
      - **Stable**:  Indicates emotional consistency. Less stable characters might have mood swings or react unpredictably.
      - **Loyal**: Influences how they interact with friends and relationships.
      - **Generous**: Affects their willingness to share and help others.
      - **Extrovert**: Determines how outgoing and social they are.
      - **Compassionate**: Impacts their empathy and concern for others.
      - **IQ**:  Influences the complexity of their thoughts and communication.
    
    **Current Mood**: Affects the general tone and content of posts and interactions. For example, a 'Hungry' character might mention food. A 'Diseased' character might express complaints or concerns about their health.
    
     **Energy Level**: affects the characters activity levels, a lower energy character may be lazier
    
    **Social Battery**: Affects how social the character is feeling, low social battery will make the character less talkative
    
    **Stress Level**: Affects how the character expresses themselves, high stress will lead to irritation
    
    **Interests and Hobbies**:  Topics they are passionate about and might post about.
    
    **Bad habits**:  Things they might jokingly refer to or that could cause problems.
    
    **Phobias**:  Things they will actively avoid or react strongly to.
    
    **Diet**: Might influence posts about food.
    
    **Favourite foods**:  Things they might mention or post about.
    
    When generating content, consider the platform (Instagram, Twitter, WhatsApp) and tailor the style accordingly. For example, Instagram posts might include visual descriptions, Twitter posts are short and opinionated, and WhatsApp messages are conversational.
    """,)
except ImportError:
    print("Warning: google-generativeai library not found. Content generation will be limited.")
    model = None

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

DNA_FILE = os.path.join(DATA_DIR, "dna_main.jsonl")
INSTAGRAM_HISTORY_FILE = os.path.join(DATA_DIR, "instagram_history.json")
TWITTER_HISTORY_FILE = os.path.join(DATA_DIR, "twitter_history.json")
WHATSAPP_HISTORY_FILE = os.path.join(DATA_DIR, "whatsapp_history.json")
RANDOM_EVENTS_FILE = os.path.join(DATA_DIR, "random_events.json")
SUPPORTING_CHARS_DIR = os.path.join(DATA_DIR, "supporting_characters")
RELATIONSHIP_FILE = os.path.join(DATA_DIR, "relationships.json")
os.makedirs(SUPPORTING_CHARS_DIR, exist_ok=True)

# Modified load function to handle both json and jsonl
def load_character_dna(filepath: str) -> Dict[str, Any]:
    """Loads character's DNA from a JSON or JSONL file."""
    if os.path.exists(filepath):
        try:
           if filepath.endswith(".jsonl"):
                with open(filepath, 'r') as f:
                  for line in f:
                     return json.loads(line)
           else:
              with open(filepath, 'r') as f:
                  return json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {filepath}. Ensure it's valid JSON/JSONL.")
            return {}
    return {}


def save_character_dna(filepath: str, data: Dict[str, Any]):
    """Saves character's DNA to a JSON or JSONL file."""
    if filepath.endswith(".jsonl"):
        with open(filepath, 'w') as f:
            json.dump(data, f)
            f.write('\n')
    else:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

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
            char_data = load_character_dna(filepath)  # Updated to use our load function
            if char_data and 'name' in char_data: #check if 'name' key exists
               characters[char_data['name']] = char_data
    return characters


def generate_gemini_content(prompt: str) -> str:
    """Generates content using Google's Gemini AI and extracts the main content."""
    if model:
        try:
            full_prompt = f"{prompt}"
            response = model.generate_content(full_prompt)

            if response.text:
                lines = response.text.split('\n')
                actual_text = ""
                extraction_started = False

                if "instagram" in prompt.lower():
                    caption_started = False
                    visual_description_started = False
                    for line in lines:
                        line = line.strip()
                        if line.lower().startswith("caption:"):
                            caption_started = True
                            actual_text += line[len("caption:").strip()]
                        elif line.lower().startswith("visual description:"):
                            visual_description_started = True
                            actual_text += " " + line[len("visual description:").strip()]
                        elif caption_started and not visual_description_started:
                            actual_text += line + " "
                        elif visual_description_started:
                            actual_text += line + " "
                    return actual_text.strip()

                elif "twitter" in prompt.lower():
                    for line in lines:
                        line = line.strip()
                        if line.lower().startswith("tweet:"):
                            return line[len("tweet:").strip()]
                    return response.text.strip() # If no "Tweet:" prefix, return the whole response

                else:
                    return response.text.strip() # For other prompts, return the whole response
            return ""
        except Exception as e:
            print(f"Error generating content with Gemini: {e}")
            return ""
    else:
        return "Gemini API not available."

def format_datetime(dt: datetime) -> str:
    """Formats a datetime object into a readable string."""
    return dt.strftime("%dth %b %Y %I:%M%p").replace("AM", "am").replace("PM","pm")

class CharacterSimulator:
    def __init__(self):
        self.dna = load_character_dna(DNA_FILE)  # Updated load function here
        self.instagram_history = load_json(INSTAGRAM_HISTORY_FILE)
        self.twitter_history = load_json(TWITTER_HISTORY_FILE)
        self.whatsapp_history = load_json(WHATSAPP_HISTORY_FILE)
        self.random_events = load_json(RANDOM_EVENTS_FILE)
        self.supporting_characters = load_supporting_characters()
        self.name = self.dna.get("Basic Information", {}).get("Name", "AI Character")
        self.relationships = load_json(RELATIONSHIP_FILE)  # Load relationships
    
    def _get_character_context(self, character_dna):
       """Creates a string with character context for the llm prompt"""
       context = f"The character's name is {character_dna.get('Basic Information',{}).get('Name','Unknown')}. "
       context += f"Their personality traits are: {character_dna.get('Personality', {}).get('Positive characteristics', [])} , negative traits are {character_dna.get('Personality', {}).get('Negative characteristics', [])} , they often use the words: {character_dna.get('Personality',{}).get('Words often used',[])} and also other words that they might use are: {character_dna.get('Personality',{}).get('Other words that might be used',[])} . "
       context += f"Their current mood is: {character_dna.get('current_mood', 'Neutral')}, their energy level is {character_dna.get('energy_level', 5)} , their social battery level is {character_dna.get('social_battery',5)} and their stress level is {character_dna.get('stress_level',5)}. "
       context += f"They enjoy the hobbies: {', '.join(character_dna.get('Hobbies', []))}. Their diet is {character_dna.get('Diet', 'unknown')} and their favourite foods are {', '.join(character_dna.get('Favourite foods', []))}"
       return context


    def _get_random_supporting_character(self):
        if self.supporting_characters:
           
            available_characters = list(self.supporting_characters.values())
            
            if not self.relationships:
               return random.choice(available_characters)
            
            weights = []
            for char in available_characters:
               if char["name"] in self.relationships:
                  weights.append(self.relationships[char["name"]]["interaction_frequency"])
               else:
                  weights.append(0.1)
            
            
            return random.choices(available_characters, weights=weights, k=1)[0]
        return None

    def _generate_social_media_post(self, platform: str):
        """Generates a social media post."""
        prompt_prefix = f"You are simulating a social media post for {self.name}."
        character_context = self._get_character_context(self.dna)
        
        if platform == "Instagram":
             
            prompt_describe = f"{prompt_prefix} {character_context} Generate a short description of the post including the item in the photo and the emotion, like 'posted a picture of their new dog while looking happy', limit to 12 words"

            description = generate_gemini_content(prompt_describe)
            
            prompt_content = f"{prompt_prefix} {character_context} Based on the post description : '{description}', generate a short caption for the post. Include a suggestion for a visual description (if not using real images). The response should start with 'Caption:' and should be followed by the caption. And should be followed by 'Visual Description:' and then the visual description."
            content = generate_gemini_content(prompt_content)
            return {"description": description, "content": content}


        elif platform == "Twitter":
            prompt_content = f"{prompt_prefix} {character_context} Generate a short, opinionated Tweet (no more than 280 characters). The response should start with 'Tweet:' followed by the tweet content."
            content = generate_gemini_content(prompt_content)
            return {"content": content}

    def _generate_whatsapp_message(self, recipient_dna: Dict[str, Any]):
        """Generates a WhatsApp message."""
        recipient_name = recipient_dna.get('Basic Information', {}).get('Name', 'Unknown')
        
        sender_context = self._get_character_context(self.dna)
        reciever_context = self._get_character_context(recipient_dna)
        
        prompt = f"You are simulating a whatsapp message. {sender_context} The main character wants to message {recipient_name} who is {reciever_context}. Simulate a short Whatsapp message from {self.name} to {recipient_name}."
        message = generate_gemini_content(prompt)
        return message

    def simulate_instagram_post(self):
        post_data = self._generate_social_media_post("Instagram")
        post_content = post_data.get('content', 'Error generating content')
        post_description = post_data.get('description', 'Error generating description')
        likes = random.randint(10, 300)
        comments = []
        num_comments = random.randint(0, 5)
        
        for _ in range(num_comments):
          commenter = self._get_random_supporting_character()
          if commenter:
                
            commenter_context = self._get_character_context(commenter)
            
            relationship = self.relationships.get(commenter["name"],{}).get("relationship", "unknown")
            
            prompt = f"You are simulating a comment on an instagram post. The post description is {post_description} and the content is '{post_content}'. {commenter_context} Simulate a short comment from {commenter['name']} in response to the post. The relationship with the poster is : {relationship}"
            comment_text = generate_gemini_content(prompt) if model else "Nice post!"
            comments.append({"author": commenter['name'], "text": comment_text})
            
        post = {"timestamp": datetime.now(), "description": post_description ,"content": post_content, "likes": likes, "comments": comments}
        self.instagram_history.append(post)
        save_json(INSTAGRAM_HISTORY_FILE, self.instagram_history)
        return post

    def simulate_twitter_post(self):
        post_data = self._generate_social_media_post("Twitter")
        post_content = post_data.get('content', "Error generating tweet")
        post = {"timestamp": datetime.now(), "content": post_content}
        self.twitter_history.append(post)
        save_json(TWITTER_HISTORY_FILE, self.twitter_history)
        return post

    def simulate_whatsapp_chat(self):
        recipient = self._get_random_supporting_character()
        if not recipient:
            return None

        message_to_recipient = self._generate_whatsapp_message(recipient)
        self.whatsapp_history.append({
            "timestamp": datetime.now(),
            "sender": self.name,
            "recipient": recipient['name'],
            "message": message_to_recipient
        })

        
        sender_context = self._get_character_context(self.dna)
        reciever_context = self._get_character_context(recipient)
        prompt = f"You are simulating a whatsapp message response. {sender_context} The main character message was '{message_to_recipient}'. {reciever_context} Simulate a short Whatsapp message from {recipient['name']} to {self.name} in response to the above message."
        response_message = generate_gemini_content(prompt) if model else "Okay."
        self.whatsapp_history.append({
            "timestamp": datetime.now(),
            "sender": recipient['name'],
            "recipient": self.name,
            "message": response_message
        })

        save_json(WHATSAPP_HISTORY_FILE, self.whatsapp_history)
        return self.whatsapp_history[-2:] 

    def simulate_daily_routine(self):
        hour = datetime.now().hour
        event = None
        
        #Try to load the random events
        random_events_data = load_json(RANDOM_EVENTS_FILE)
        if isinstance(random_events_data, dict) and "events" in random_events_data:
          events = random_events_data["events"]
          if random.random() < 0.2:
                chosen_event = random.choices(events, weights=[event["probability"] for event in events])[0]
                
                
                prompt = f"Simulate a daily event where {self.name} is {chosen_event['name']}. Include details of the event, such as the location, the involved people from the list: {', '.join([char['name'] for char in self.supporting_characters.values()])}, and what happened. Limit to 3 sentences."
                event_details = generate_gemini_content(prompt)
                involved_chars = [char for char in self.supporting_characters.values() if char["name"] in event_details]
                if "log" not in random_events_data:
                  random_events_data["log"] = []
                random_events_data["log"].append({
                    "timestamp": datetime.now(),
                    "name": chosen_event["name"],
                    "details": event_details,
                    "involved_characters": [char["name"] for char in involved_chars],
                })
                save_json(RANDOM_EVENTS_FILE, random_events_data)
                return chosen_event['name']
        
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
            if not isinstance(random_events_data, dict):
                random_events_data = {"log": []}
            elif "log" not in random_events_data:
                random_events_data["log"] = []
            random_events_data["log"].append({"timestamp": datetime.now(), "event": event})
            save_json(RANDOM_EVENTS_FILE, random_events_data)
            return event
        return None
    
    def update_character_state(self):
      
      mood_choices = ["Happy", "Tired", "Hungry", "Stressed","Relaxed", "Neutral", f"Diseased: {random.choice(['Flu', 'Cold', 'Fever'])}"]
      self.dna["current_mood"]= random.choice(mood_choices)
      self.dna["energy_level"]= max(1,min(10,self.dna.get("energy_level", 5)+ random.randint(-1,1)))
      self.dna["social_battery"]= max(1,min(10,self.dna.get("social_battery", 5)+ random.randint(-1,1)))
      self.dna["stress_level"]= max(1,min(10,self.dna.get("stress_level", 5)+ random.randint(-1,1)))
      save_character_dna(DNA_FILE,self.dna)
      

    def run_daily_updates(self):
        
        self.update_character_state()
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
                simulator.supporting_characters = load_supporting_characters()
                st.success(f"Supporting character '{new_char_name}' created.")
                st.experimental_rerun()

st.header("Social Media Feed")
platform = st.selectbox("Select Platform", ["Instagram", "Twitter", "WhatsApp", "Daily Events"])

if platform == "Instagram":
    st.subheader("Instagram")
    for post in reversed(simulator.instagram_history):
        # Convert timestamp string to datetime object
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
        # Convert timestamp string to datetime object
        timestamp_obj = datetime.fromisoformat(tweet['timestamp'])
        st.write(f"**{simulator.name}** - {format_datetime(timestamp_obj)}")
        st.write(tweet['content'])
        st.markdown("---")

elif platform == "WhatsApp":
    st.subheader("WhatsApp")
    for message in simulator.whatsapp_history:
        sender = message['sender']
        text = message['message']
        # Convert timestamp string to datetime object
        timestamp_obj = datetime.fromisoformat(message['timestamp'])
        st.write(f"**{sender}**: {text}  *({format_datetime(timestamp_obj)} )*")

elif platform == "Daily Events":
    st.subheader("Daily Events")
    events_data = load_json(RANDOM_EVENTS_FILE)
    if isinstance(events_data, dict) and "log" in events_data:
        for event in reversed(events_data["log"]):
            # Convert timestamp string to datetime object (handle potential missing timestamp)
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
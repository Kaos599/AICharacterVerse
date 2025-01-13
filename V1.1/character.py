# character.py
import random
from datetime import datetime
from typing import Dict, Any, List
from data_handler import load_character_dna, save_character_dna, load_json, save_json, load_supporting_characters
from gemini_integration import generate_gemini_content
from config import DNA_FILE, INSTAGRAM_HISTORY_FILE, TWITTER_HISTORY_FILE, WHATSAPP_HISTORY_FILE, RANDOM_EVENTS_FILE, SUPPORTING_CHARS_DIR, RELATIONSHIP_FILE

class CharacterSimulator:
    def __init__(self):
        self.dna = load_character_dna(DNA_FILE)
        self.instagram_history = load_json(INSTAGRAM_HISTORY_FILE)
        self.twitter_history = load_json(TWITTER_HISTORY_FILE)
        self.whatsapp_history = load_json(WHATSAPP_HISTORY_FILE)
        self.random_events = load_json(RANDOM_EVENTS_FILE)
        self.supporting_characters = load_supporting_characters(SUPPORTING_CHARS_DIR)
        self.name = self.dna.get("Basic Information", {}).get("Name", "AI Character")
        self.relationships = load_json(RELATIONSHIP_FILE)

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
        """Simulates creating an Instagram post with interactions from supporting characters."""
        post_data = self._generate_social_media_post("Instagram")
        timestamp = datetime.now().isoformat()
        
        # Generate a random number of likes
        likes = random.randint(50, 200)
        
        # Generate comments from supporting characters
        comments = []
        num_comments = random.randint(2, 5)  # Random number of initial comments
        
        used_characters = set()  # Track which characters have commented
        
        for _ in range(num_comments):
            # Filter out characters who have already commented
            available_characters = [char for char in self.supporting_characters 
                                if char['name'] not in used_characters]
            
            if not available_characters:
                break
                
            # Select a random character who hasn't commented yet
            commenter = random.choice(available_characters)
            used_characters.add(commenter['name'])
            
            # Generate comment based on character's personality
            comment_prompt = f"""
            You are {commenter['name']}, with the following traits:
            Personality: {commenter['personality']}
            Current mood: {commenter.get('current_mood', 'Neutral')}
            
            Generate a realistic, short comment (1-2 sentences) for this Instagram post:
            {post_data['content']}
            
            The comment should reflect your personality and current mood.
            """
            
            comment_text = generate_gemini_content(comment_prompt)
            
            comments.append({
                'author': commenter['name'],
                'text': comment_text,
                'timestamp': timestamp
            })
        
        post = {
            'timestamp': timestamp,
            'author': self.name,
            'content': post_data['content'],
            'likes': likes,
            'comments': comments,
            'gemini_data': post_data.get('gemini_data', {})
        }
        
        self.instagram_history.append(post)
        self._save_instagram_history()

    def simulate_twitter_post(self):
        post_data = self._generate_social_media_post("Twitter")
        post_content = post_data.get('content', "Error generating tweet")
        post = {"timestamp": datetime.now().isoformat(), "content": post_content}
        self.twitter_history.append(post)
        save_json(TWITTER_HISTORY_FILE, self.twitter_history)
        return post

    def simulate_whatsapp_chat(self):
        recipient = self._get_random_supporting_character()
        if not recipient:
            return None

        message_to_recipient = self._generate_whatsapp_message(recipient)
        self.whatsapp_history.append({
            "timestamp": datetime.now().isoformat(),
            "sender": self.name,
            "recipient": recipient['name'],
            "message": message_to_recipient
        })

        sender_context = self._get_character_context(self.dna)
        reciever_context = self._get_character_context(recipient)
        prompt = f"You are simulating a whatsapp message response. {sender_context} The main character message was '{message_to_recipient}'. {reciever_context} Simulate a short Whatsapp message from {recipient['name']} to {self.name} in response to the above message."
        response_message = generate_gemini_content(prompt) if generate_gemini_content else "Okay."
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
                    "timestamp": datetime.now().isoformat(),
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
            random_events_data["log"].append({"timestamp": datetime.now().isoformat(), "event": event})
            save_json(RANDOM_EVENTS_FILE, random_events_data)
            return event
        return None
        
    def simulate_supporting_character_post(self):
        """Simulates a random supporting character creating an Instagram post."""
        # Randomly select a supporting character to post
        poster = random.choice(self.supporting_characters)
        
        # Generate post content based on character's personality
        post_prompt = f"""
        You are {poster['name']}, with the following traits:
        Personality: {poster['personality']}
        Current mood: {poster.get('current_mood', 'Neutral')}
        
        Generate an Instagram post. The response should include:
        - A caption that reflects your personality and current mood
        - A visual description of what the photo would show
        
        Start the caption with "Caption:" and the visual description with "Visual Description:"
        """
        
        post_content = generate_gemini_content(post_prompt)
        timestamp = datetime.now().isoformat()
        
        # Generate initial likes and comments
        likes = random.randint(30, 150)
        comments = []
        
        # Main character might comment
        if random.random() < 0.7:  # 70% chance
            comment_prompt = f"""
            You are {self.name}, with your unique personality.
            Generate a short comment (1-2 sentences) for this Instagram post by {poster['name']}:
            {post_content}
            """
            main_char_comment = generate_gemini_content(comment_prompt)
            comments.append({
                'author': self.name,
                'text': main_char_comment,
                'timestamp': timestamp
            })
        
        post = {
            'timestamp': timestamp,
            'author': poster['name'],
            'content': post_content,
            'likes': likes,
            'comments': comments
        }
        
        self.instagram_history.append(post)
        self._save_instagram_history()

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
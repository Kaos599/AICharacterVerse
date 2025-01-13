import random
from datetime import datetime
from typing import Dict, Any, List
from data_handler import load_character_dna, save_character_dna, load_json, save_json, load_supporting_characters, backfill_last_update
from gemini_integration import generate_gemini_content
from config import DNA_FILE, INSTAGRAM_HISTORY_FILE, TWITTER_HISTORY_FILE, WHATSAPP_HISTORY_FILE, RANDOM_EVENTS_FILE, SUPPORTING_CHARS_DIR, RELATIONSHIP_FILE
import uuid

class CharacterSimulator:
    def __init__(self):
        
        backfill_last_update(INSTAGRAM_HISTORY_FILE)

        
        self.dna = load_character_dna(DNA_FILE)
        self.instagram_history = load_json(INSTAGRAM_HISTORY_FILE)
        self.twitter_history = load_json(TWITTER_HISTORY_FILE)
        self.whatsapp_history = load_json(WHATSAPP_HISTORY_FILE)
        self.random_events = load_json(RANDOM_EVENTS_FILE)
        self.supporting_characters = load_supporting_characters(SUPPORTING_CHARS_DIR)
        self.name = self.dna.get("Basic Information", {}).get("Name", "AI Character")
        self.relationships = load_json(RELATIONSHIP_FILE)
        self._available_characters = []
        self._refresh_available_characters()
        
    def _refresh_available_characters(self):
        """Refreshes the list of available supporting character names."""
        self.supporting_characters = load_supporting_characters(SUPPORTING_CHARS_DIR)
        self.relationships = load_json(RELATIONSHIP_FILE)
        self._available_characters = list(self.relationships.keys()) 

    def _get_random_supporting_character(self):
        if not self._available_characters:
            print("WARNING: No available supporting characters. Returning None.")
            return None

        char_name = random.choice(self._available_characters) 
        char_data = self.supporting_characters.get(char_name)
        if not char_data:  
            print(f"WARNING: Data not found for {char_name}. Returning None")
            return None

        return char_data  


    def _get_character_context(self, character_dna):
       """Creates a string with character context for the llm prompt"""
       context = f"The character's name is {character_dna.get('Basic Information',{}).get('Name','Unknown')}. "
       context += f"Their personality traits are: {character_dna.get('Personality', {}).get('Positive characteristics', [])} , negative traits are {character_dna.get('Personality', {}).get('Negative characteristics', [])} , they often use the words: {character_dna.get('Personality',{}).get('Words often used',[])} and also other words that they might use are: {character_dna.get('Personality',{}).get('Other words that might be used',[])} . "
       context += f"Their current mood is: {character_dna.get('current_mood', 'Neutral')}, their energy level is {character_dna.get('energy_level', 5)} , their social battery level is {character_dna.get('social_battery',5)} and their stress level is {character_dna.get('stress_level',5)}. "
       context += f"They enjoy the hobbies: {', '.join(character_dna.get('Hobbies', []))}. Their diet is {character_dna.get('Diet', 'unknown')} and their favourite foods are {', '.join(character_dna.get('Favourite foods', []))}"
       return context

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

    def _should_interact(self, char1_name, char2_name, relationship_strength):
        """Determines if two characters should interact based on mood and relationship."""

        char1_data = self.supporting_characters.get(char1_name)
        char2_data = self.supporting_characters.get(char2_name)


        base_chance = relationship_strength / 100

        social_modifier = char1_data.get('social_battery', 5) / 10

        mood_map = {
            'Happy': 1.2,
            'Excited': 1.3,
            'Content': 1.0,
            'Neutral': 0.8,
            'Tired': 0.6,
            'Irritated': 0.4,
            'Angry': 0.2
        }
        mood_modifier = mood_map.get(char1_data.get('current_mood', 'Neutral'), 0.8)

        interaction_chance = base_chance * social_modifier * mood_modifier

        print(f"DEBUG: Interaction check for {char1_name} and {char2_name}:")
        print(f"DEBUG:   Relationship Strength: {relationship_strength}")
        print(f"DEBUG:   Social Modifier: {social_modifier}")
        print(f"DEBUG:   Mood Modifier: {mood_modifier}")
        print(f"DEBUG:   Interaction Chance: {interaction_chance}")
        result = random.random() < interaction_chance
        print(f"DEBUG:   Result: {result}")
        return result

    def _generate_comment_thread(self, post, initial_comment, max_depth=3):
        thread = [initial_comment]
        current_depth = 0

        commenters = set()  

        while current_depth < max_depth:
            last_comment = thread[-1]
            commenters.add(last_comment['author'])  

            potential_responders = [
                char_name for char_name in self._available_characters
                if char_name != last_comment['author'] and char_name not in commenters
            ]

            if last_comment['author'] != self.name and self.name not in commenters:
                potential_responders.append(self.name)
            
            if not potential_responders:
                break 

            
            best_friend_name = next((name for name, rel in self.relationships.items() if rel.get("relationship_type") == "Best Friend"), None)
            if best_friend_name and best_friend_name in potential_responders and best_friend_name not in commenters:
                responder_name = best_friend_name
                potential_responders.remove(responder_name) 
            elif potential_responders:
              responder_name = random.choice(potential_responders)
            else:
              break
            
            responder_data = self.supporting_characters.get(responder_name)
            commenter_data = self.supporting_characters.get(last_comment['author'])

            if responder_data and commenter_data:
                relationship_strength = self.relationships.get(responder_name, {}).get("interaction_frequency", 0.5) * 100
                if self._should_interact(responder_name, last_comment['author'], relationship_strength):

                    if self._should_interact(responder_name, last_comment['author'], relationship_strength):
                        response_prompt = f"""
                    You are {responder_name}, responding to this comment: "{last_comment['text']}" by {last_comment['author']} on the post: "{post['content']}"

                    Your relationship with {last_comment['author']} is {relationship_strength}/100.
                    Your current mood is {responder_data.get('current_mood', 'Neutral')}.

                    Generate a natural, short response that reflects your personality,
                    mood, and relationship with the commenter.
                    Keep it under 2 sentences.
                    """
                        response_text = generate_gemini_content(response_prompt)

                        thread.append({
                            'author': responder_name,  
                            'text': response_text,
                            'timestamp': datetime.now().isoformat(),
                            'parent_id': last_comment.get('id'),
                            'id': str(uuid.uuid4())
                        })

                        if random.random() < 0.7 - (current_depth * 0.2):
                            break
                elif not commenter_data:
                    print(f"DEBUG: Commenter data not found for {last_comment['author']}")
                elif not responder_data:
                    print(f"DEBUG: Responder data not found for {responder_name}")

            current_depth += 1

        return thread

    def simulate_instagram_post(self):
            """Simulates creating an Instagram post with interactive comment threads."""
            post_data = self._generate_social_media_post("Instagram")
            timestamp = datetime.now().isoformat()

            post = {
                'timestamp': timestamp,
                'author': self.name,
                'content': post_data['content'],
                'likes': random.randint(50, 200),
                'comments': [],
            }

            print(f"DEBUG: Before refreshing in simulate_instagram_post, _available_characters length: {len(self._available_characters)}")
            self._refresh_available_characters()
            print(f"DEBUG: After refreshing in simulate_instagram_post, _available_characters length: {len(self._available_characters)}")

            num_initial_comments = random.randint(2, 4)

            if self._available_characters:
                print(f"DEBUG: Available characters before generating comments: {self._available_characters}")
                for _ in range(num_initial_comments):
                    commenter_name = random.choice(self._available_characters)
                    print(f"DEBUG: Attempting comment from: {commenter_name}")  
                    commenter_data = self.supporting_characters.get(commenter_name)

                    if commenter_data:
                        print(f"DEBUG: Commenter data found for {commenter_name}")  
                        relationship_strength = self.relationships.get(commenter_name, {}).get("interaction_frequency", 0.5) * 100
                        should_interact = self._should_interact(commenter_name, self.name, relationship_strength) 
                        print(f"DEBUG: Should {commenter_name} interact? {should_interact}")  
                        if should_interact:
                            comment_prompt = f"""
                            You are {commenter_name}, with these traits:
                            Personality: {commenter_data.get('Personality', {})}
                            Current mood: {commenter_data.get('current_mood', 'Neutral')}

                            Generate a natural comment for this Instagram post:
                            {post_data['content']}
                            """

                            initial_comment = {
                                'author': commenter_name,
                                'text': generate_gemini_content(comment_prompt),
                                'timestamp': timestamp,
                                'id': str(uuid.uuid4())
                            }

                            thread = self._generate_comment_thread(post, initial_comment)
                            post['comments'].extend(thread)
                        else:
                            print(f"DEBUG: {commenter_name} did not interact.")  
                    else:
                        print(f"DEBUG: Commenter data NOT found for {commenter_name}")  

            post['last_update'] = timestamp
            self.instagram_history.append(post)
            self._save_instagram_history()

    def update_post_interactions(self):
        """Updates post interactions periodically."""
        current_time = datetime.now()

        for post in self.instagram_history:
            last_update = post.get('last_update', None)  
            if last_update:
                last_update = datetime.fromisoformat(last_update)
                if (current_time - last_update).total_seconds() < 5:
                    continue  

            self._refresh_available_characters()  

            commenter_name = random.choice(self._available_characters)
            commenter_data = self.supporting_characters.get(commenter_name)

            if commenter_data and random.random() < 0.9 and self._should_interact(commenter_name, post['author'],
                                    self.relationships.get(commenter_name, {}).get("interaction_frequency", 0.5) * 100):

                comment_prompt = f"""
                    You are {commenter_name}, discovering this post:
                    {post['content']}

                    Generate a natural, initial comment.
                    """
                initial_comment = {
                    'author': commenter_name,
                    'text': generate_gemini_content(comment_prompt),
                    'timestamp': current_time.isoformat(),
                    'id': str(uuid.uuid4())
                }
                thread = self._generate_comment_thread(post, initial_comment)
                post.setdefault('comments', []).extend(thread)

            post['last_update'] = current_time.isoformat()  

        self._save_instagram_history()


    def simulate_twitter_post(self):
        post_data = self._generate_social_media_post("Twitter")
        post_content = post_data.get('content', "Error generating tweet")
        timestamp = datetime.now().isoformat()

        post = {
            "timestamp": timestamp,
            "author": self.name,
            "content": post_content,
            "replies": [],
            "likes": random.randint(10, 50),
            'id': str(uuid.uuid4())  
        }

        print(f"DEBUG: Starting Twitter post simulation. Available characters: {self._available_characters}")
        self._refresh_available_characters()
        num_initial_replies = random.randint(1, 3)

        if self._available_characters:
            print(f"DEBUG: Available characters for Twitter replies: {self._available_characters}")
            for _ in range(num_initial_replies):
                replier_name = random.choice(self._available_characters)
                print(f"DEBUG: Attempting reply from: {replier_name}")
                replier_data = self.supporting_characters.get(replier_name)

                if replier_data:
                    print(f"DEBUG: Replier data found for {replier_name}")
                    relationship_strength = self.relationships.get(replier_name, {}).get("interaction_frequency", 0.5) * 100
                    should_interact = self._should_interact(replier_name, self.name, relationship_strength)
                    print(f"DEBUG: Should {replier_name} reply? {should_interact}")
                    if should_interact:
                        reply_prompt = f"""
                        You are {replier_name}.
                        The following is a tweet by {self.name}: "{post_content}"
                        Generate a short, natural reply to this tweet (under 280 characters).
                        """
                        initial_reply = {
                            'author': replier_name,
                            'text': generate_gemini_content(reply_prompt),
                            'timestamp': timestamp,
                            'id': str(uuid.uuid4()),
                            'parent_id': post['id']
                        }
                        post['replies'].append(initial_reply) 
                    else:
                        print(f"DEBUG: {replier_name} did not reply.")
                else:
                    print(f"DEBUG: Replier data NOT found for {replier_name}")

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

        random_events_data = load_json(RANDOM_EVENTS_FILE)
        if isinstance(random_events_data, dict) and "events" in random_events_data:
          events = random_events_data["events"]
          if random.random() < 0.2:
                chosen_event = random.choices(events, weights=[event["probability"] for event in events])[0]

                prompt = f"Simulate a daily event where {self.name} is {chosen_event['name']}. Include details of the event, such as the location, the involved people from the list: {', '.join([char['name'] for char in self._available_characters])}, and what happened. Limit to 3 sentences."
                event_details = generate_gemini_content(prompt)
                involved_chars = [char for char in self._available_characters if char["name"] in event_details]
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

        if not self._available_characters:
            return

        poster_name = random.choice(self._available_characters)
        poster_data = self.supporting_characters.get(poster_name)

        if poster_data:
            post_prompt = f"""
            You are {poster_name}, with the following traits:
            Personality: {poster_data.get('Personality', {})}
            Current mood: {poster_data.get('current_mood', 'Neutral')}

            Generate an Instagram post. The response should include:
            - A caption that reflects your personality and current mood
            - A visual description of what the photo would show

            Start the caption with "Caption:" and the visual description with "Visual Description:"
            """

            post_content = generate_gemini_content(post_prompt)
            timestamp = datetime.now().isoformat()

            likes = random.randint(30, 150)
            comments = []

            if random.random() < 0.7:
                comment_prompt = f"""
                You are {self.name}, with your unique personality.
                Generate a short comment (1-2 sentences) for this Instagram post by {poster_name}:
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
                'author': poster_name,
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

    def _save_instagram_history(self):
        save_json(INSTAGRAM_HISTORY_FILE, self.instagram_history)
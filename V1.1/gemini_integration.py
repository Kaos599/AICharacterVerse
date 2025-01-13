# gemini_integration.py
import os
try:
    import google.generativeai as genai
    from config import CHARACTER_SYSTEM_INSTRUCTIONS

    genai.configure(api_key=os.environ.get("AIzaSyBEWgDXRyFMHJpXG9bHZZFyDDKDYVEWY2k"))
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
    model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp", generation_config=generation_config, system_instruction=CHARACTER_SYSTEM_INSTRUCTIONS)
except ImportError:
    print("Warning: google-generativeai library not found. Content generation will be limited.")
    model = None

def generate_gemini_content(prompt: str) -> str:
    """Generates content using Google's Gemini AI and extracts the main content."""
    if model:
        try:
            full_prompt = f"{prompt}"
            response = model.generate_content(full_prompt)

            if response.text:
                lines = response.text.split('\n')

                if "instagram" in prompt.lower():
                    caption_started = False
                    visual_description_started = False
                    actual_text = ""
                    for line in lines:
                        line = line.strip()
                        if line.lower().startswith("caption:"):
                            caption_started = True
                            actual_text += line[len("caption:").strip():]
                        elif line.lower().startswith("visual description:"):
                            visual_description_started = True
                            actual_text += " " + line[len("visual description:").strip():]
                        elif caption_started and not visual_description_started:
                            actual_text += line + " "
                        elif visual_description_started:
                            actual_text += line + " "
                    return actual_text.strip()

                elif "twitter" in prompt.lower():
                    for line in lines:
                        line = line.strip()
                        if line.lower().startswith("tweet:"):
                            return line[len("tweet:").strip():]
                    return response.text.strip()

                # New logic to extract just the comment
                elif "generate a natural comment" in prompt.lower() or "respond to this comment" in prompt.lower():
                    for line in lines:
                        line = line.strip()
                        # Return the first line that isn't empty or a plan item
                        if line and not line.lower().startswith("plan:") and not line.startswith("*"):
                            return line
                    return response.text.strip() # Fallback

                else:
                    return response.text.strip()
            return ""
        except Exception as e:
            print(f"Error generating content with Gemini: {e}")
            return ""
    else:
        return "Gemini API not available."
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
    model = genai.GenerativeModel(model_name="gemini-2.0-flash-thinking-exp-1219", generation_config=generation_config, system_instruction=CHARACTER_SYSTEM_INSTRUCTIONS)
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
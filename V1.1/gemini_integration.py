# gemini_integration.py
import os
try:
    import google.generativeai as genai
    from google.ai.generativelanguage_v1beta.types import content
    from config import CHARACTER_SYSTEM_INSTRUCTIONS
    import json

    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
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

            if "generate a natural comment" in prompt.lower() or "respond to this comment" in prompt.lower():
                try:
                    comment_model = genai.GenerativeModel(
                        model_name="gemini-2.0-flash-exp",
                        generation_config={
                            **model.generation_config,
                            "response_mime_type": "application/json",
                        },
                        system_instruction=CHARACTER_SYSTEM_INSTRUCTIONS
                    )
                    response = comment_model.generate_content(full_prompt)
                    json_response = json.loads(response.text.strip())  # Strip whitespace and load JSON
                    return json_response.get("comment", "").strip()
                except (json.JSONDecodeError, AttributeError) as e:
                    print(f"Error decoding JSON comment: {response.text}. Error: {e}")
                    return ""

            else:
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

                    else:
                        return response.text.strip()
                return ""
        except Exception as e:
            print(f"Error generating content with Gemini: {e}")
            return ""
    else:
        return "Gemini API not available."
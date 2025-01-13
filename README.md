# Dynamic AI Character Social Media Simulator

This project simulates the online presence of a dynamic AI character across various social media platforms like Instagram, Twitter, and WhatsApp. The character's personality, daily routines, and relationships influence the content of their posts and interactions, creating a believable and diverse online life.

## Getting Started

Follow these instructions to run the AI character simulator on your local machine.

### Prerequisites

* **Python 3.7+:** Make sure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
* **pip:** Python's package installer. It usually comes with Python.
* **A Google Gemini API Key:** You'll need an API key from Google AI to generate the social media content. You can obtain one by following the instructions on the [Google AI for Developers site](https://ai.google.dev/).

### Installation and Setup

1. **Download the `V1.2` folder:** This folder contains the latest working version of the project. You can download it directly from the repository interface.

2. **Navigate to the `V1.2` directory:** Open your terminal or command prompt and navigate to the downloaded `V1.2` folder. For example:
   ```bash
   cd path/to/your/downloaded/V1.2
   ```

3. **Create a virtual environment (recommended):** This helps isolate the project's dependencies.
   ```bash
   python -m venv venv
   ```
   Activate the virtual environment:
   * **On Windows:**
     ```bash
     .\venv\Scripts\activate
     ```
   * **On macOS and Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:** Install the required Python libraries using pip.
   ```bash
   pip install google-generativeai streamlit python-dotenv schedule
   ```

5. **Set up your Gemini API Key**

### Running the Simulator

Once you have completed the installation and setup, you can run the Streamlit application, which provides the user interface for the simulator:

```bash
streamlit run streamlit.py
```

This command will start the Streamlit app, and you should see it open in your web browser. You can then interact with the UI to simulate the AI character's social media activity.

## Project Structure (within the `V1.2` folder)

* **`config.py`:**  Contains configuration settings for the project, including file paths and the system instructions for the AI model.
* **`character.py`:**  Implements the `CharacterSimulator` class, which contains the core logic for simulating the AI character's behavior, generating posts, and handling interactions.
* **`data_handler.py`:** Handles loading and saving data (character DNA, social media histories, etc.) from JSON files.
* **`gemini_integration.py`:**  Manages the integration with the Google Gemini AI API for generating text content.
* **`streamlit.py`:**  Creates the Streamlit web application for interacting with the simulator.
* **`utils.py`:** Contains utility functions, such as date and time formatting.
* **`data/`:**  This directory contains the data files used by the simulator:
    * **`dna_main.jsonl`:**  Defines the main AI character's characteristics and personality.
    * **`instagram_history.json`:** Stores the history of simulated Instagram posts.
    * **`twitter_history.json`:** Stores the history of simulated Twitter posts.
    * **`whatsapp_history.json`:** Stores the history of simulated WhatsApp chats.
    * **`random_events.json`:** Stores the log of simulated daily routine events.
    * **`supporting_characters/`:**  Contains JSON files defining the characteristics of supporting characters.
    * **`relationships.json`:** Defines the relationships between the main character and supporting characters.
* **`requirements.txt`:** Lists the Python packages that need to be installed.

## How it Works

The AI character's behavior is driven by its "DNA" defined in `dna_main.jsonl`. The `CharacterSimulator` class uses this DNA, along with simulated daily routines and interactions with other characters, to generate content using the Google Gemini API. The Streamlit interface allows you to trigger these simulations and view the resulting social media feeds.

Enjoy simulating the dynamic life of your AI character!


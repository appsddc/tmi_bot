import os
from google import genai
from google.genai import types

def analyze_transcript(transcript_text):
    # Initialize the modern 2026 Client
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # We now use gemini-2.0-flash for speed and reliability
    model_id = "gemini-2.5-flash"

    # Define the Scout persona using the proper Config object
    config = types.GenerateContentConfig(
        system_instruction="""
        You are the 'TMI Signal Scout.' 
        High-density filter for Irish Macro-Economics, Infrastructure (EirGrid), and Planning.
        Analyze the transcript and provide a scored 'Signal Report' (0-100%).
        Focus on technical density and 'links' to the Irish context.
        """
    )

    try:
        # In 2026, we pass the config as a named argument
        response = client.models.generate_content(
            model=model_id,
            contents=transcript_text[:30000],
            config=config
        )
        return response.text
    except Exception as e:
        # If the model name changes again, this will tell us exactly what's available
        return f"Sieve Error: {str(e)}"

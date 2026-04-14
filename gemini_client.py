from google import genai

from config import config_obj

client = genai.Client(api_key=config_obj.gemini_api_key)


def get_answer_from_gemeni(prompt: str):
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )
    return response.text

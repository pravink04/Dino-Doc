"""GenAI layer: the LLM only explains numbers we computed. Works with Groq or Gemini (both have free tiers)."""
import os
from dotenv import load_dotenv

load_dotenv()
PROVIDER = os.getenv("AI_PROVIDER", "groq").lower()
SYSTEM = ("You are a senior business analyst writing for executives. Use ONLY the facts provided. "
          "Copy numbers and the currency symbol exactly as written: never convert, rescale or add words like 'million'. "
          "If the facts say cost data is missing, do not discuss profit or margin. "
          "If a period is marked partial, say the comparison is unreliable. "
          "If the facts do not answer the question, say so. Be concise and specific.")


def ask_ai(prompt):
    try:
        if PROVIDER == "groq":
            from groq import Groq
            key = os.getenv("GROQ_API_KEY")
            if not key:
                return "Add GROQ_API_KEY to your .env file."
            r = Groq(api_key=key).chat.completions.create(
                model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
                messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
                max_tokens=800, temperature=0.2)
            return r.choices[0].message.content

        if PROVIDER == "gemini":
            from google import genai
            from google.genai import types
            key = os.getenv("GEMINI_API_KEY")
            if not key:
                return "Add GEMINI_API_KEY to your .env file."
            r = genai.Client(api_key=key).models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), contents=prompt,
                config=types.GenerateContentConfig(system_instruction=SYSTEM, temperature=0.2))
            return r.text

        return "Set AI_PROVIDER to groq or gemini in your .env file."
    except Exception as e:  # rate limit, wrong key, wrong model name, no internet
        return f"AI error: {e}"
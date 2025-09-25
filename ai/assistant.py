"""
AI-ассистент: отвечает на вопросы, объясняет стратегии, помогает подобрать blend.
(Вставь свой ключ OpenAI или используем локальный LLM)
"""
import openai

OPENAI_API_KEY = "ВСТАВЬ_СВОЙ_OPENAI_API_KEY"

def ask_ai(prompt):
    openai.api_key = OPENAI_API_KEY
    resp = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct", prompt=prompt, max_tokens=200
    )
    return resp["choices"][0]["text"]
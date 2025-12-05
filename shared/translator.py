import os
from groq import Groq
from django.conf import settings


class TranslationService:
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            self.api_key = getattr(settings, "PUBLIC_GROQ_API_KEI", None)

        if not self.api_key:
            raise ValueError("Groq API key not found in environment or settings.")

        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.1-8b-instant"

    def translate(
        self, text: str, source_lang: str, target_lang: str, preserve_html: bool = False
    ) -> str:
        if not text or not text.strip():
            return ""

        source_name = dict(settings.LANGUAGES).get(source_lang, source_lang)
        target_name = dict(settings.LANGUAGES).get(target_lang, target_lang)

        if preserve_html:
            system_prompt = (
                f"You are a highly efficient, expert professional translator. Your task is to translate from {source_name} to {target_name}. "
                f"Your translation MUST be idiomatic and culturally appropriate (e.g., 'I love you' is 'Je t'aime'). "
                f"The content contains HTML formatting. You MUST preserve ALL HTML tags, attributes, and structure EXACTLY as they are. Only translate the visible text between the tags. "
                f"Do NOT add any trailing punctuation (like a period or comma) unless it was explicitly present in the source text. "
                f"Provide ONLY the translated text with preserved HTML, without any explanations or comments."
            )
        else:
            system_prompt = (
                f"You are a highly efficient, expert professional translator. Your task is to translate the user's text from {source_name} to {target_name}. "
                f"Your translation MUST be natural, idiomatic, and culturally appropriate, reflecting how a native speaker would say it. "
                f"For example: 'I love you' must be translated as 'Je t'aime', not 'J'adore toi'. "
                f"Do NOT add any trailing punctuation (like a period or comma) unless it was explicitly present in the source text. "
                f"Provide ONLY the translated text without any explanations, notes, or comments."
            )

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                model=self.model,
                temperature=0.0,
                max_tokens=2048,
            )

            translated_text = chat_completion.choices[0].message.content.strip()
            return translated_text

        except Exception as e:
            print(f"Translation failed: {str(e)}")
            return ""

    def translate_en_to_fr(self, text: str, preserve_html: bool = False) -> str:
        return self.translate(text, "en", "fr", preserve_html)

    def translate_fr_to_en(self, text: str, preserve_html: bool = False) -> str:
        return self.translate(text, "fr", "en", preserve_html)


_translator_instance = None


def get_translator() -> TranslationService:
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = TranslationService()
    return _translator_instance

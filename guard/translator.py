import os
from groq import Groq
from django.conf import settings


class TranslationService:
    def __init__(self):
        self.api_key = getattr(settings, 'PUBLIC_GROQ_API_KEI', None)
        if not self.api_key:
            raise ValueError("PUBLIC_GROQ_API_KEI not found in Django settings")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.1-8b-instant"
    
    def translate(self, text: str, source_lang: str, target_lang: str, preserve_html: bool = False) -> str:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code ('en' or 'fr')
            target_lang: Target language code ('en' or 'fr')
            preserve_html: Whether to preserve HTML formatting
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return ""
        
        source_name = 'English' if source_lang == 'en' else 'French'
        target_name = 'English' if target_lang == 'en' else 'French'
        
        if preserve_html:
            system_prompt = (
                f"You are an expert professional translator specializing in {source_name} to {target_name} translation. "
                f"Your translations are natural, idiomatic, and culturally appropriate - not literal word-for-word translations. "
                f"The text contains HTML formatting. You MUST preserve ALL HTML tags, attributes, and structure EXACTLY as they are. "
                f"Only translate the text content between the tags. Never translate HTML tag names, attributes, or code. "
                f"Provide ONLY the translated text with preserved HTML formatting, without any explanations, notes, or comments."
            )
        else:
            system_prompt = (
                f"You are an expert professional translator specializing in {source_name} to {target_name} translation. "
                f"Your translations are natural, idiomatic, and culturally appropriate - not literal word-for-word translations. "
                f"Translate naturally as a native speaker would say it, considering context and common usage. "
                f"For example, 'I love you' in English should be 'Je t'aime' in French, not 'J'adore toi'. "
                f"Provide ONLY the translated text without any explanations, notes, or comments."
            )
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                model=self.model,
                temperature=0.5,
                max_tokens=2048,
            )
            
            translated_text = chat_completion.choices[0].message.content.strip()
            return translated_text
            
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")
    
    def translate_en_to_fr(self, text: str, preserve_html: bool = False) -> str:
        return self.translate(text, 'en', 'fr', preserve_html)
    
    def translate_fr_to_en(self, text: str, preserve_html: bool = False) -> str:
        return self.translate(text, 'fr', 'en', preserve_html)

_translator_instance = None

def get_translator() -> TranslationService:
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = TranslationService()
    return _translator_instance

from googletrans import Translator
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
class TranslatorService:
    def __init__(self):
        self.translator = Translator()

    def translate(self, text: str, target_language: str) -> str:
        try:
            translation = self.translator.translate(text, dest=target_language)
            return translation.text
        except Exception as e:
            logging.error(f"Translation error: {str(e)}")
            return "[translation failed]"
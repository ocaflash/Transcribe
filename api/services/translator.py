from googletrans import Translator

class TranslatorService:
    def __init__(self):
        self.translator = Translator()

    def translate(self, text: str, target_language="en"):
        if target_language.lower() == "en":
            return text

        try:
            translation = self.translator.translate(text, dest=target_language)
            return translation.text
        except Exception as e:
            return "[translation failed]"

from .audio_processor import AudioProcessor
from .translator import TranslatorService

def transcribe_audio(file_path: str, target_language="en") -> dict:
    processor = AudioProcessor(file_path)
    final_transcription = processor.process_audio()

    translator = TranslatorService()
    result = {
        "original_text": final_transcription,
        "translation": {
            target_language: translator.translate(final_transcription, target_language),
            "ru": translator.translate(final_transcription, "ru")
        }
    }

    return result

from utils.audio_processor import AudioProcessor
from utils.translator import TranslatorService
from langdetect import detect

def transcribe_audio(file_path: str, target_language="en") -> dict:
    processor = AudioProcessor(file_path)
    final_transcription = processor.process_audio()

    original_language = detect(final_transcription)

    translator = TranslatorService()
    result = {
        "original_text": final_transcription,
        "original_language": original_language,
        "translation": {}
    }

    if original_language!=target_language:
        result["translation"][target_language] = translator.translate(final_transcription, target_language)

    if original_language!="ru":
        result["translation"]["ru"] = translator.translate(final_transcription, "ru")

    return result

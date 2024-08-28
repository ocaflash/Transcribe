from utils.audio_processor import AudioProcessor
from utils.translator import TranslatorService
from langdetect import detect
from repositories.file_repository import FileRepository

def transcribe_audio(file_path: str, file_id: int, file_repository: FileRepository, target_language="en") -> dict:
    processor = AudioProcessor(file_path, file_id, file_repository)

    file_repository.update_file_status(file_id, "transcribing")
    final_transcription = processor.process_audio()

    original_language = detect(final_transcription)

    file_repository.update_file_status(file_id, "translating")
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

    file_repository.update_file_status(file_id, "completed")
    return result
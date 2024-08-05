from utils.audio_converter import AudioConverter
from utils.audio_splitter import AudioSplitter
from utils.speech_recognizer import SpeechRecognizer
from repositories.file_repository import FileRepository
import logging

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self, file_path: str, file_id: int, file_repository: FileRepository):
        self.file_path = file_path
        self.file_id = file_id
        self.file_repository = file_repository
        self.converter = AudioConverter(file_path)
        self.wav_file_path = self.converter.convert_to_wav()
        self.splitter = AudioSplitter(self.wav_file_path)
        self.recognizer = SpeechRecognizer()


    def process_audio(self):
        segments = self.splitter.split_audio()
        transcribed_texts = []

        total_segments = len(segments)
        for i, segment in enumerate(segments):
            text = self.recognizer.recognize_speech(segment, i)
            transcribed_texts.append(text)

            # Обновляем статус в базе данных
            progress = int((i + 1) / total_segments * 100)
            self.file_repository.update_file_status(self.file_id, f"processing:{progress}")

        final_transcription = " ".join(filter(None, transcribed_texts))

        # Обновляем статус по завершении обработки
        self.file_repository.update_file_status(self.file_id, "completed")

        return final_transcription
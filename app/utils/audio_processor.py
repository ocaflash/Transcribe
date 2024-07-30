import speech_recognition as sr
import os
from pydub import AudioSegment
import magic
import logging
import subprocess

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self, file_path: str):
        if not isinstance(file_path, str):
            raise TypeError(f"Expected a string, got {type(file_path).__name__}")
        self.file_path = file_path
        self.wav_file_path = self.convert_to_wav()


    def get_audio_format(self):
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(self.file_path)
        return file_type.split('/')[-1] if file_type.startswith('audio/') else None


    def convert_to_wav(self):
        if not isinstance(self.file_path, str):
            raise TypeError(f"Expected self.file_path to be a string, got {type(self.file_path).__name__}")

        audio_format = self.get_audio_format()
        if audio_format=='wav':
            return self.file_path

        wav_path = self.file_path.rsplit('.', 1)[0] + '.wav'

        try:
            # Используем subprocess для вызова ffmpeg напрямую
            subprocess.run(['ffmpeg', '-i', self.file_path, wav_path], check=True)
            logger.info(f"Successfully converted {self.file_path} to {wav_path}")
            return wav_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error converting file: {e}")
            raise


    def split_audio(self, segment_length_ms=25000):
        audio = AudioSegment.from_wav(self.wav_file_path)
        return [audio[i:i + segment_length_ms] for i in range(0, len(audio), segment_length_ms)]


    def process_audio(self):
        segments = self.split_audio()
        recognizer = sr.Recognizer()
        transcribed_texts = []

        for i, segment in enumerate(segments):
            segment_path = f"/tmp/segment_{i}.wav"
            segment.export(segment_path, format="wav")

            with sr.AudioFile(segment_path) as source:
                audio = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio)
                except sr.RequestError as e:
                    logger.error(f"Could not request results from Google Speech Recognition service; {e}")
                    text = None
                except sr.UnknownValueError:
                    logger.warning(f"Google Speech Recognition could not understand audio segment {i}")
                    text = "[recognition failed]"

            transcribed_texts.append(text)
            os.remove(segment_path)

        final_transcription = " ".join(filter(None, transcribed_texts))
        if self.wav_file_path!=self.file_path:
            os.remove(self.wav_file_path)

        return final_transcription
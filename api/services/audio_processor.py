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

        wav_path = self.file_path.rsplit('.', 1)[0] + '.wav'
        try:
            command = [
                'ffmpeg', '-i', self.file_path,
                '-ar', '16000', '-ac', '1',
                wav_path
            ]
            result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
            if result.returncode!=0:
                logger.error(f"ffmpeg error: {result.stderr}")
                raise RuntimeError(f"ffmpeg error: {result.stderr}")
        except Exception as e:
            logger.error(f"Error converting to WAV: {str(e)}")
            raise
        return wav_path


    def split_audio(self, segment_length_ms=30000):
        try:
            audio = AudioSegment.from_wav(self.wav_file_path)
        except Exception as e:
            logger.error(f"Error loading WAV file: {str(e)}")
            raise

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
                    text = "[recognition failed]"
                    logger.error(f"RequestError during recognition: {str(e)}")
                except sr.UnknownValueError:
                    text = "[recognition failed]"
                    logger.error("UnknownValueError during recognition")

            transcribed_texts.append(text)
            os.remove(segment_path)

        final_transcription = " ".join(transcribed_texts)
        if self.wav_file_path != self.file_path:
            os.remove(self.wav_file_path)

        return final_transcription

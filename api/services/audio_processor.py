import speech_recognition as sr
import os
from pydub import AudioSegment
import magic

class AudioProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.wav_file_path = self.convert_to_wav()

    def get_audio_format(self):
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(self.file_path)
        return file_type.split('/')[-1] if file_type.startswith('audio/') else None

    def convert_to_wav(self):
        audio_format = self.get_audio_format()
        if audio_format == 'wav':
            return self.file_path

        wav_path = self.file_path.rsplit('.', 1)[0] + '.wav'
        audio = AudioSegment.from_file(self.file_path, format=audio_format)
        audio.export(wav_path, format="wav")
        return wav_path

    def split_audio(self, segment_length_ms=30000):
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
                    text = None
                except sr.UnknownValueError:
                    text = "[recognition failed]"

            transcribed_texts.append(text)
            os.remove(segment_path)

        final_transcription = " ".join(transcribed_texts)
        if self.wav_file_path != self.file_path:
            os.remove(self.wav_file_path)

        return final_transcription

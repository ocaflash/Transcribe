import speech_recognition as sr
import os
import logging

logger = logging.getLogger(__name__)

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def recognize_speech(self, audio_segment, segment_index):
        segment_path = f"/tmp/segment_{segment_index}.wav"
        audio_segment.export(segment_path, format="wav")

        with sr.AudioFile(segment_path) as source:
            audio = self.recognizer.record(source)
            try:
                text = self.recognizer.recognize_google(audio)
            except sr.RequestError as e:
                logger.error(f"Could not request results from Google Speech Recognition service; {e}")
                text = None
            except sr.UnknownValueError:
                logger.warning(f"Google Speech Recognition could not understand audio segment {segment_index}")
                text = "[recognition failed]"

        os.remove(segment_path)
        return text
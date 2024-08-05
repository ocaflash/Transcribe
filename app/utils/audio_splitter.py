from pydub import AudioSegment

class AudioSplitter:
    def __init__(self, wav_file_path: str):
        self.wav_file_path = wav_file_path

    def split_audio(self, segment_length_ms=25000):
        audio = AudioSegment.from_wav(self.wav_file_path)
        return [audio[i:i + segment_length_ms] for i in range(0, len(audio), segment_length_ms)]
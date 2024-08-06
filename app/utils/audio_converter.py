import subprocess
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class AudioConverter:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def convert_to_wav(self) -> str:

        base, ext = os.path.splitext(self.file_path)

        if ext.lower() == '.wav':
            logger.info(f"File {self.file_path} is already in WAV format.")
            return self.file_path

        wav_path = base + '.wav'

        try:
            subprocess.run(['ffmpeg', '-i', self.file_path, wav_path], check=True)
            logger.info(f"Successfully converted {self.file_path} to {wav_path}")
            return wav_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error converting file: {e}")
            raise
import subprocess
import logging

logger = logging.getLogger(__name__)

class AudioConverter:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def convert_to_wav(self) -> str:
        wav_path = self.file_path.rsplit('.', 1)[0] + '.wav'
        try:
            subprocess.run(['ffmpeg', '-i', self.file_path, wav_path], check=True)
            logger.info(f"Successfully converted {self.file_path} to {wav_path}")
            return wav_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error converting file: {e}")
            raise
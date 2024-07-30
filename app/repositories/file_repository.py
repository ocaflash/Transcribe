from sqlalchemy.orm import Session
from models import File, Transcription

class FileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_file(self, filename: str, file_type: str, file_path: str, status: str):
        db_file = File(
            filename=filename,
            file_type=file_type,
            file_path=file_path,
            status=status
        )
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        return db_file

    def create_transcription(self, file_id: int, text: str, language: str):
        transcription = Transcription(
            file_id=file_id,
            text=text,
            language=language
        )
        self.db.add(transcription)
        self.db.commit()
        self.db.refresh(transcription)
        return transcription

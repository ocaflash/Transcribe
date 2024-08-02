from sqlalchemy.orm import Session
from models import File, Transcription
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FileRepository:
    def __init__(self, db: Session):
        self.db = db


    def create_file(self, filename: str, file_type: str, file_path: str, status: str, drive_file_id: str, drive_file_link: str, description: str = None, tag: str = None):
        db_file = File(
            filename=filename,
            file_type=file_type,
            file_path=file_path,
            status=status,
            upload_date=datetime.utcnow(),
            drive_file_id=drive_file_id,
            drive_file_link=drive_file_link,
            description=description,
            tag=tag
        )
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        return db_file


    def create_transcription(self, file_id: int, text: str, language: str, translated_text: str):
        transcription = Transcription(
            file_id=file_id,
            text=text,
            language=language,
            translated_text=translated_text,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(transcription)
        self.db.commit()
        self.db.refresh(transcription)
        logger.info(f"Created transcription: id={transcription.id}, file_id={file_id}")
        return transcription

    def get_all_files(self):
        return self.db.query(File).all()
    def get_file_by_id(self, file_id: int):
        return self.db.query(File).filter(File.id == file_id).first()

    def get_transcription_by_file_id(self, file_id: int):
        return self.db.query(Transcription).filter(Transcription.file_id == file_id).first()

    def update_file_status(self, file_id: int, new_status: str):
        file = self.get_file_by_id(file_id)
        if file:
            file.status = new_status
            self.db.commit()
            self.db.refresh(file)
        return file
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_type = Column(String)
    file_path = Column(String)
    status = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)

    transcriptions = relationship("Transcription", back_populates="file")

class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    text = Column(Text)
    language = Column(String)
    translated_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    file = relationship("File", back_populates="transcriptions")
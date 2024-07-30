from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from models import File as FileModel, Transcription as TranscriptionModel
from database import get_db
from services.transcription import transcribe_audio
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        logger.debug(f"File saved at: {file_location}")

        # Transcribe the file
        transcription_result = transcribe_audio(file_location)
        logger.debug(f"Transcription result: {transcription_result}")

        if transcription_result["original_text"] == "" or transcription_result["original_text"] == "[recognition failed]":
            return {"error": "Speech recognition failed", "details": transcription_result}

        db_file = FileModel(
            filename=file.filename,
            file_type=file.content_type,
            file_path=file_location,
            status="transcribed"
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        db_transcription = TranscriptionModel(
            file_id=db_file.id,
            text=transcription_result["original_text"],
            language=transcription_result.get("original_language", "unknown")
        )
        db.add(db_transcription)
        db.commit()

        # Remove temporary file
        os.remove(file_location)

        return {
            "filename": file.filename,
            "status": "transcribed",
            "original_text": transcription_result["original_text"],
            "original_language": transcription_result.get("original_language", "unknown"),
            "translated_text": transcription_result["translation"].get("ru", "[translation failed]")
        }
    except Exception as e:
        logger.error(f"Error in upload_file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


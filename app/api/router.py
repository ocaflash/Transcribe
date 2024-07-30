from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from services.transcription import transcribe_audio
from repositories.file_repository import FileRepository
from database import get_db
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/api/v1/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_repository = FileRepository(db)

    try:
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        logger.info(f"File saved at: {file_location}")

        # Transcribe the file
        logger.info(f"Starting transcription for file: {file_location}")
        transcription_result = transcribe_audio(file_location)
        logger.info(f"Transcription completed. Result: {transcription_result}")

        if transcription_result["original_text"] == "" or transcription_result["original_text"] == "[recognition failed]":
            logger.warning(f"Speech recognition failed for file: {file_location}")
            return {"error": "Speech recognition failed", "details": transcription_result}

        db_file = file_repository.create_file(
            filename=file.filename,
            file_type=file.content_type,
            file_path=file_location,
            status="transcribed"
        )

        file_repository.create_transcription(
            file_id=db_file.id,
            text=transcription_result["original_text"],
            language=transcription_result.get("original_language", "unknown")
        )

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
        logger.exception(f"Error in upload_file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

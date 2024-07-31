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

        # Create file record in database
        db_file = file_repository.create_file(
            filename=file.filename,
            file_type=file.content_type,
            file_path=file_location,
            status="uploaded"
        )

        # Transcribe the file
        logger.info(f"Starting transcription for file: {file_location}")
        transcription_result = transcribe_audio(file_location)
        logger.info(f"Transcription completed. Result: {transcription_result}")

        if transcription_result["original_text"] == "" or transcription_result["original_text"] == "[recognition failed]":
            logger.warning(f"Speech recognition failed for file: {file_location}")
            file_repository.update_file_status(db_file.id, "failed")
            return {"error": "Speech recognition failed", "details": transcription_result}

        # Update file status and create transcription record
        file_repository.update_file_status(db_file.id, "transcribed")
        translated_text = transcription_result["translation"].get("ru", "[translation failed]")
        transcription = file_repository.create_transcription(
            file_id=db_file.id,
            text=transcription_result["original_text"],
            language=transcription_result.get("original_language", "unknown"),
            translated_text=translated_text
        )

        # Remove temporary file
        os.remove(file_location)

        return {
            "file_id": db_file.id,
            "filename": file.filename,
            "status": "transcribed",
            "original_text": transcription_result["original_text"],
            "original_language": transcription_result.get("original_language", "unknown"),
            "translated_text": translated_text
        }
    except Exception as e:
        logger.exception(f"Error in upload_file: {str(e)}")
        if 'db_file' in locals():
            file_repository.update_file_status(db_file.id, "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/file/{file_id}")
async def get_file_info(file_id: int, db: Session = Depends(get_db)):
    file_repository = FileRepository(db)
    file = file_repository.get_file_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    transcription = file_repository.get_transcription_by_file_id(file_id)

    return {
        "file_id": file.id,
        "filename": file.filename,
        "status": file.status,
        "upload_date": file.upload_date,
        "transcription": transcription.text if transcription else None,
        "language": transcription.language if transcription else None,
        "translated_text": transcription.translated_text if transcription else None
    }
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from database import get_db
from repositories.file_repository import FileRepository
from fastapi.responses import StreamingResponse
from services.transcription import transcribe_audio
from utils.google_drive import upload_file_to_drive, delete_file_from_drive
import asyncio, json, random, os, logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/api/v1/upload")
async def upload_file(
        file: UploadFile = File(...),
        description: str = Form(None),
        tag: str = Form(None),
        db: Session = Depends(get_db)
):
    file_repository = FileRepository(db)

    try:
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        logger.info(f"File saved at: {file_location}")

        # Upload to Google Drive
        drive_file_id, drive_file_link = upload_file_to_drive(file_location, file.filename)

        # Create file record in database
        db_file = file_repository.create_file(
            filename=file.filename,
            file_type=file.content_type,
            file_path=file_location,
            status="uploaded",
            drive_file_id=drive_file_id,
            drive_file_link=drive_file_link,
            description=description,
            tag=tag
        )

        # Transcribe the file
        logger.info(f"Starting transcription for file: {file_location}")
        transcription_result = transcribe_audio(file_location, db_file.id, file_repository)
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
            "drive_file_link": drive_file_link,
            "description": description,
            "tag": tag,
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
        "drive_file_link": file.drive_file_link,
        "language": transcription.language if transcription else None,
        "transcription": transcription.text if transcription else None,
        "tag": file.tag,
        "translated_text": transcription.translated_text if transcription else None
    }

@router.post("/api/v1/settings")
async def save_settings(
    google_drive_folder: str = Form(...),
    db: Session = Depends(get_db)
):
    # Here you would save the settings to a configuration file or database
    # For now, we'll just log the received setting
    logger.info(f"Received new Google Drive Folder ID: {google_drive_folder}")
    return {"message": "Settings saved successfully"}

@router.delete("/api/v1/file/{file_id}")
async def delete_file(file_id: int, db: Session = Depends(get_db)):
    file_repository = FileRepository(db)
    file = file_repository.get_file_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete from Google Drive
    if file.drive_file_id:
        delete_file_from_drive(file.drive_file_id)

    # Delete from database
    file_repository.delete_file(file_id)

    # Delete local file if it exists
    if os.path.exists(file.file_path):
        os.remove(file.file_path)

    return {"message": "File deleted successfully"}

@router.get("/api/v1/file-processing-status/{file_id}")
async def file_processing_status(file_id: int, request: Request, db: Session = Depends(get_db)):
    file_repository = FileRepository(db)
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            file = file_repository.get_file_by_id(file_id)
            if file.status=="completed":
                yield f"data: {json.dumps({'status': file.status, 'progress': 100})}\n\n"
                break
            yield f"data: {json.dumps({'status': file.status, 'progress': calculate_progress(file)})}\n\n"
            await asyncio.sleep(1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")
def calculate_progress(file):
    if file.status == "uploaded":
        return 0
    elif file.status == "completed":
        return 100
    elif file.status.startswith("processing:"):
        try:
            # Извлекаем процент из статуса, если он там есть
            return int(file.status.split(":")[1])
        except (IndexError, ValueError):
            # Если не удалось извлечь процент, возвращаем примерное значение
            return 50
    elif file.status == "transcribing":
        # Предполагаем, что транскрибирование занимает примерно 60% всего процесса
        return 30
    elif file.status == "translating":
        # Предполагаем, что перевод занимает примерно 30% всего процесса
        return 70
    else:
        # Для неизвестных статусов возвращаем 0
        return 0

@router.put("/api/v1/file/{file_id}")
async def update_file(
    file_id: int,
    description: str = Form(None),
    tag: str = Form(None),
    db: Session = Depends(get_db)
):
    file_repository = FileRepository(db)
    file = file_repository.get_file_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if description is not None:
        file.description = description
    if tag is not None:
        file.tag = tag

    db.commit()
    db.refresh(file)

    return {"message": "File updated successfully"}

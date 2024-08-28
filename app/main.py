from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from api.router import router as api_router
from database import get_db
from repositories.file_repository import FileRepository
from models import Transcription

app = FastAPI()
app.include_router(api_router)

# Монтируем директорию для статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/upload")
async def upload(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/")
@app.get("/files")
async def file_list(request: Request, db: Session = Depends(get_db)):
    file_repository = FileRepository(db)
    files = file_repository.get_all_files()

    for file in files:
        transcriptions = file.transcriptions
        if transcriptions:
            file.transcription = transcriptions[0].text
            file.translated_text = transcriptions[0].translated_text
        else:
            file.transcription = "No transcription available."
            file.translated_text = "No translation available."

    return templates.TemplateResponse("file_list.html", {"request": request, "files": files})

@app.get("/file/{file_id}")
async def file_details(request: Request, file_id: int, db: Session = Depends(get_db)):
    file_repository = FileRepository(db)
    file = file_repository.get_file_by_id(file_id)

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    transcriptions = file.transcriptions
    transcription_text = "No transcription available."
    translated_text = "No translation available."

    if transcriptions:
        transcription_text = transcriptions[0].text
        translated_text = transcriptions[0].translated_text

    return templates.TemplateResponse("file_details.html", {
        "request": request,
        "file": file,
        "transcription_text": transcription_text,
        "translated_text": translated_text
    })

@app.get("/settings")
async def settings(request: Request):
    google_drive_folder_id = "your_current_folder_id"
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "google_drive_folder_id": google_drive_folder_id
    })
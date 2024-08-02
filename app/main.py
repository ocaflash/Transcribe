# app/main.py
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from api.router import router as api_router
from database import get_db
from repositories.file_repository import FileRepository

app = FastAPI()
app.include_router(api_router)

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/upload")
async def upload(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/files")
async def file_list(request: Request, db: Session = Depends(get_db)):
    file_repository = FileRepository(db)
    files = file_repository.get_all_files()
    return templates.TemplateResponse("file_list.html", {"request": request, "files": files})

@app.get("/file/{file_id}")
async def file_details(request: Request, file_id: int, db: Session = Depends(get_db)):
    file_repository = FileRepository(db)
    file = file_repository.get_file_by_id(file_id)
    return templates.TemplateResponse("file_details.html", {"request": request, "file": file})

@app.get("/settings")
async def settings(request: Request):
    # You might want to load the current settings from a configuration file or database
    google_drive_folder_id = "your_current_folder_id"
    return templates.TemplateResponse("settings.html", {"request": request, "google_drive_folder_id": google_drive_folder_id})
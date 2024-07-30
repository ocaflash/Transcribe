from fastapi import FastAPI
from database import engine
from models import Base
from routes import files

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(files.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the Transcription API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

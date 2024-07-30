# Dockerfile
FROM python:3.9

WORKDIR /api

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y ffmpeg libmagic1

COPY . /api

ENV PYTHONPATH=/api

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

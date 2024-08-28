FROM python:3.12.5

WORKDIR /app

RUN pip install poetry
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

RUN apt-get update && apt-get install -y ffmpeg libmagic1

COPY . /app

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
FROM python:3.11-slim

WORKDIR /opt/orbit

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY orbit ./orbit
COPY migrations ./migrations
COPY alembic.ini pyproject.toml ./

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
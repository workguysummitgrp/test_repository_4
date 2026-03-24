FROM python:3.12-slim

WORKDIR /opt/service

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy into backend/ subdirectory to preserve "from backend.app" import paths
COPY . ./backend

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

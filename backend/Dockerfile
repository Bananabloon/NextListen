FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    sqlite3 \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /backend
#WORKDIR /backend/backendApps dla gunicorn, odhashować tu, docker-compose i w settings, wszystko podpisane. Jak będziemy robić migracje na produkcje
COPY /backendApps/ ./backendApps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 


#CMD ["gunicorn", "backendApps.wsgi:application", "--bind", "0.0.0.0:8000"] wersja dla gunicorn(gorszy debug)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

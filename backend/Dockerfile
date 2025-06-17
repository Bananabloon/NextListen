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

WORKDIR /backend/backendApps

COPY /backendApps/ ./backendApps
COPY requirements.txt .
#COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
#RUN chmod +x /usr/local/bin/wait-for-it.sh
RUN pip install --no-cache-dir -r requirements.txt 


#CMD ["gunicorn", "backendApps.wsgi:application", "--bind", "0.0.0.0:8000"] for gunicorn
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

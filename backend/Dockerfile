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

WORKDIR /backendApps

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

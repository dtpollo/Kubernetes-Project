FROM python:3.10-slim

# Install build dependencies needed for cryptography
RUN apt-get update && apt-get install -y netcat-openbsd gcc libmariadb-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-it.sh ./wait-for-it.sh
RUN chmod +x wait-for-it.sh

COPY . .

CMD ["python", "app/main.py"]


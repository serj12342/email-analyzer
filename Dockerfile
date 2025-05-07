FROM python:3.11

RUN apt-get update && apt-get install -y \
    unzip zip p7zip-full curl \
    libmagic1 libfuzzy-dev \
    build-essential python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    mail-parser requests oletools pefile yara-python rarfile py7zr \
    yandex-cloud-ml-sdk watchdog

# 🔧 Копируем исходный код проекта в контейнер
WORKDIR /app
COPY . /app

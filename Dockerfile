# Dockerfile
FROM python:3.11

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    unzip zip rar unrar p7zip-full \
    libmagic1 libfuzzy-dev libemu-dev \
    build-essential python3-dev \
    && rm -rf /var/lib/apt/lists/*


# Установка Python-зависимостей
RUN pip install --no-cache-dir \
    git+https://github.com/buffer/thug.git \
    mail-parser requests oletools pefile yara-python rarfile py7zr \
    yandex-cloud

WORKDIR /app

COPY . /app
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

FROM python:3.11-slim

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирование всех скриптов
COPY *.py ./

# Копирование папок с вложениями
COPY malicious_attachments ./malicious_attachments
COPY legitimate_attachments ./legitimate_attachments

# Пользователь для безопасности
RUN useradd -m -u 1000 attacker && \
    chown -R attacker:attacker /app

# Создаем директорию для сохранения файлов и даем права пользователю
RUN mkdir -p /app/sent_attachments && \
    chown -R attacker:attacker /app/sent_attachments && \
    chmod 755 /app/sent_attachments

USER attacker

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV TARGET_EMAIL=operator1@financepro.ru
ENV SMTP_SERVER=front
ENV SMTP_PORT=25

# Точка входа
CMD ["python3", "mixed_phishing.py"]

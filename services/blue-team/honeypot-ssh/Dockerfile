FROM python:3.10-slim-bookworm
WORKDIR /app
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --default-timeout=1000 --no-cache-dir -r requirements.txt
COPY . .
# Expose the internal port
EXPOSE 2222
CMD ["python", "-u", "main.py"]
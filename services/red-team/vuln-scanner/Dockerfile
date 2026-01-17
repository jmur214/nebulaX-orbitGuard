FROM python:3.10-slim-bookworm

WORKDIR /app

# Install Nmap binary
RUN apt-get update && apt-get install -y nmap && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "-u", "main.py"]
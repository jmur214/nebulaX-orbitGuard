FROM python:3.10-slim-bookworm

WORKDIR /app

COPY requirements.txt .
# Install dependencies
# We install 'skyfield' which pulls standard astronomy data files
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]
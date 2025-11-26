FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
# Install dependencies
# We install 'skyfield' which pulls standard astronomy data files
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]
FROM nebulax-python-base:latest
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Flask runs on 5000 by default
CMD ["python", "main.py"]

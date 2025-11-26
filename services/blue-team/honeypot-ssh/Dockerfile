FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Expose the internal port
EXPOSE 2222
CMD ["python", "-u", "main.py"]
FROM nebulax-python-base:latest
WORKDIR /app
# Postgres client libs (libpq-dev) and gcc are already in the shared base.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

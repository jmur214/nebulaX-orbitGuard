FROM nebulax-python-base:latest
WORKDIR /app
COPY requirements.txt .
# Skyfield + scikit-learn + pandas + matplotlib are service-specific heavy deps
# and stay in the per-service requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-u", "main.py"]

FROM nebulax-python-base:latest
WORKDIR /app
# nmap binary is service-specific; not worth baking into the shared base.
RUN apt-get update && apt-get install -y --no-install-recommends nmap \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-u", "main.py"]

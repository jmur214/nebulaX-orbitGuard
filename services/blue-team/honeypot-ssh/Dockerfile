FROM nebulax-python-base:latest
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 2222
CMD ["python", "-u", "main.py"]

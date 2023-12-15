FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/power_button.py .
ENV CONFIG_DIR=/app/config
EXPOSE 5000
ENTRYPOINT ["python", "power_button.py"]

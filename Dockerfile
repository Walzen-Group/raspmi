FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y gcc
RUN pip install --no-cache-dir -r requirements.txt
COPY src/power_button.py .
EXPOSE 5000
ENTRYPOINT ["python", "power_button.py"]

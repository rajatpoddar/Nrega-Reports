FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

# Port 5233 expose karein
EXPOSE 5233

# Gunicorn ko 5233 par chalayein
CMD ["gunicorn", "--bind", "0.0.0.0:5233", "app:app"]
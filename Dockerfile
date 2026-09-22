FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# Говорим контейнеру открыть порт для Render
EXPOSE 10000
CMD ["python", "Sqapp.py"]

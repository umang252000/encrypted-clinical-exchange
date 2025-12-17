FROM python:3.10-slim

WORKDIR /app

COPY app /app/app

RUN pip install --no-cache-dir -r /app/app/requirements.txt

EXPOSE 8100

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]
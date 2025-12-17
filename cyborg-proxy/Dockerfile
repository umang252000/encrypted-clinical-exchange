FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy the app folder (correct path!)
COPY app /app/app

# Ensure /app is a Python package
RUN touch /app/__init__.py

# Install dependencies
RUN pip install --no-cache-dir -r /app/app/requirements.txt

EXPOSE 8000

# Run server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
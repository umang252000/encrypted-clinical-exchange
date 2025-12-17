FROM python:3.10-slim

# Create root working directory
WORKDIR /app

# Copy the app folder into the container
COPY app /app/app

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/app/requirements.txt

# Expose correct port
EXPOSE 8100

# Run FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]
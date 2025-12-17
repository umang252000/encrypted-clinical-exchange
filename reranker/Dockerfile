FROM python:3.10-slim

# --------------------------------------------
# Environment hygiene
# --------------------------------------------
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# --------------------------------------------
# App setup
# --------------------------------------------
WORKDIR /app

# Copy application package
COPY app/ ./app

# Install dependencies
RUN pip install --no-cache-dir -r app/requirements.txt

# --------------------------------------------
# Network
# --------------------------------------------
EXPOSE 8300

# --------------------------------------------
# Healthcheck (used by Docker / compose)
# --------------------------------------------
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD curl -f http://localhost:8300/health || exit 1

# --------------------------------------------
# Start service (IMPORTANT LINE)
# --------------------------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8300"]
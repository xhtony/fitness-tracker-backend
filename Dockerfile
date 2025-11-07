# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source code
COPY . .

#  Ensure Django static root exists before collectstatic
RUN mkdir -p /app/staticfiles

#  Set environment variable for Django static root (防止某些容器中settings取不到BASE_DIR路径)
ENV DJANGO_STATIC_ROOT=/app/staticfiles

#  Collect static files
#RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "fitness_tracker_backend.wsgi:application"]


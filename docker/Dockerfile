# Use an official slim Python 3.10 image as the base image.
FROM python:3.10-slim

# Ensure that Python output is not buffered (helpful for Docker logging).
ENV PYTHONUNBUFFERED=1

# Set the working directory to /app in the container.
WORKDIR /app

# Copy only the requirements file first to leverage Docker's caching.
COPY requirements.txt .

# Install Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container.
COPY . .

# Default command: run unit tests using Python's unittest discovery.
CMD ["python", "-m", "unittest", "discover", "-v"]

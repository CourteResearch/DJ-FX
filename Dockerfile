# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for audio processing (ffmpeg)
# and other build tools
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the backend requirements file into the container
COPY backend/requirements.txt .

# Install Python dependencies
# Upgrade pip, setuptools, and wheel first
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install Cython first as it's a build dependency for some packages (e.g., madmom)
RUN pip install --no-cache-dir Cython

# Install the rest of the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend application code into the container
COPY backend/ .

# Expose the port the app runs on
EXPOSE 8000

# Define environment variables for MongoDB connection
# These should be set in Render's environment variables, not hardcoded here.
# For local testing, you might use .env.example values.
# ENV MONGO_URL="your_mongo_uri"
# ENV DB_NAME="your_db_name"

# Command to run the application
# Uvicorn will serve the FastAPI app defined in server.py
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]

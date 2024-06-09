# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Setting a workdir
WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY src/app /app/

# Expose port 80 for the FastAPI application
EXPOSE 80

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

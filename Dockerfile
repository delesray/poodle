# Use an official Python runtime as a parent image
FROM python:3.12

COPY requirements.txt /app/
COPY src/app /app/

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 80 for the FastAPI application
EXPOSE 80

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
# Use an official Python runtime as a parent image
FROM python:3.12

# Setting a workdir
WORKDIR /app

# Copy and install requirements to the container
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copies the rest of the app
COPY . .

# Run
RUN alembic upgrade head

# Expose port 80 for the FastAPI application
EXPOSE 80
# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
#CMD ["alembic", "upgrade", "head"]

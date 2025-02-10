FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY src/app /app/

EXPOSE 80

# command runs when container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

FROM python:3.10-alpine
#FROM --platform=linux/amd64 python:3.11.2-alpine

RUN pip install --upgrade pip

# Install system dependencies
# RUN apk update && add libpq-dev libc-dev gcc build-base python3-dev linux-headers
RUN apk update && apk add python3-dev \
                          gcc \
                          libc-dev \
                          libffi-dev

# install prerequisites
RUN pip install poetry==1.5.1

# install dependencies
WORKDIR /api

COPY pyproject.toml poetry.lock /api/

RUN poetry config virtualenvs.create false && poetry install --no-root

# Copy the rest of the application
COPY /api .

# Command to run the application using FastAPI's Uvicorn
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
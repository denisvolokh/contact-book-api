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

# Install dockerize
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# install dependencies
WORKDIR /code

# # Set the PYTHONPATH
# ENV PYTHONPATH /

COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock

RUN poetry config virtualenvs.create false && poetry install --no-root

# Copy the rest of the application
COPY ./api /code/api

# Command to run the application using FastAPI's Uvicorn
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
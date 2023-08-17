# Solution

## 1. Database Setup Using Docker Compose

Postgres database has been created using Docker Compose to ensure a consistent and replicable development environment.

Docker Compose Service Configuration:

```yml
version: '3'

services:
...

  database:
    image: postgres:latest
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: dbname
    volumes:
      - ./pg_data:/var/lib/postgresql/data/
      - ./pg_backups:/pg_backups

...

volumes:
  pg_data: {}
  pg_backups: {}
```

## 2. Import CSV data into database

The data import script, `api/load.py`, has been crafted and encapsulated within a separate, short-lived Docker Compose service. This script ensures that the table is both created and empty before loading the data. After its execution, it reports the status of the work to the logs and then exits.

Docker Compose Service Configuration:

```yml
version: '3'

services:
...
  imports:
    build:
      context: .
      dockerfile: Dockerfile
    depends_on:
      - database
    environment:
      DATABASE_URL: postgresql://user:password@database:5432/dbname
    env_file:
      - .env
    volumes:
      - ./api:/api
    command: python3 load.py
...
```

## 3. Periodic Updates

Periodic updates of the database with external data have been implemented using the Celery library. The service allows the creation of tasks that can be executed in the background and scheduled as well. 

The task to update contacts is scheduled to run once a day at midnight.

```py
# api/tasks.py

# Schedule the task
celery.conf.beat_schedule = {
    "update-contacts": {
        "task": "tasks.task_update_contacts",
        "schedule": crontab(hour="0"),
    },
}

```

The Celery periodic updates have been encapsulated within a separate Docker Compose service.

```yml
version: '3'

services:
...
  tasks:
    build:
      context: .
      dockerfile: Dockerfile
    depends_on:
      - database
      - redis
    environment:
      DATABASE_URL: postgresql://user:password@database:5432/dbname
    env_file:
      - .env
    volumes:
      - ./api:/api
    command: celery -A tasks.celery worker --loglevel=info
...  
```


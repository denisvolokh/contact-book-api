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
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - ./pg_data:/var/lib/postgresql/data/
      - ./pg_backups:/pg_backups

...

volumes:
  pg_data: {}
  pg_backups: {}
```


## 2. Database Model

```python

class Contact(Base):
    __tablename__ = "Contact"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nimbus_id = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    description = Column(String)
    search_vector = Column(TSVECTOR)

    __table_args__ = (
        Index('idx_search_vector', search_vector, postgresql_using='gin'),
    )

```

The `Contact` model is designed to store all data from the imported CSV file. Additionally, the `nimbus_id` field has been added to store references to an external database and is used during synchronization. A `search_vector` field has also been added to store the pre-calculated search vector for full-text search.


```python
def update_search_vector(mapper, connection, target):
    values = [target.first_name, target.last_name, target.email, target.description]
    filtered_values = [item for item in values if item]
    target.search_vector = func.to_tsvector('english', " ".join(filtered_values))


event.listen(Contact, 'before_insert', update_search_vector)
event.listen(Contact, 'before_update', update_search_vector)
```

The pre-calculation of the search vector is configured using ORM event listener.



## 3. Import CSV data into database

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
    env_file:
      - .env
    volumes:
      - ./api:/api
    command: python3 load.py
...
```

## 4. Periodic Updates

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
    env_file:
      - .env
    volumes:
      - ./api:/api
    command: celery -A tasks.celery worker --loglevel=info
...  
```

## 5. Full-text Search API

### Syncronous Search

The `api/v1/search` endpoint allow to perform a full-text search in synchronous mode. The endpoint accepts a `text` query parameter and returns a list of matching contacts.

### Asynchronous Search

The `api/v2/search` endpoint allow to perform a full-text search in asynchronous mode. The endpoint accepts a `text` query parameter and returns a task id. The task id can be used to retrieve the search results.

The `api/v2/search/status/{task_id}` endpoint can be used to retrieve the search results.

## 6. Testing

The `api/tests` directory contains unit tests for the API endpoints. The tests can be executed using the following command:

```bash
docker-compose run --rm api pytest
```

## 7. Improvements

- Add service that will aggregate logs from all compose services and store them in a centralized location.
- Add service that will monitor the health of all compose services and send alerts if any of the services is down.

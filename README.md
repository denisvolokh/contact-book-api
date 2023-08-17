# Setup Local Environment

1. Install poetry with pip

```shell
pip install poetry
```

2. Activate virtual environment

```shell
poetry shell
```

3. Install dependencies

Make sure you are in the root folder

```shell
poetry install
```

4. Create and configure .env file

Create `.env` file using `.env.example` as a template and specify values for all secret keys in the file

5. Run containers

```shell
docker-compose up -d
```

6. Install pre-commits hooks (optional)

```shell
pre-commit install
```

# Swagger

[API Swagger](http://localhost:5000/swagger)

# Docs

[Project Documentation](http://localhost:8000/)
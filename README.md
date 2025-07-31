# Data Agent

This is a Python application that translates natural language to SQL queries.

## Setup

### Conda Environment

1.  **Create a new conda environment:**
    ```bash
    conda create --name data-agent python=3.11
    ```

2.  **Activate the environment:**
    ```bash
    conda activate data-agent
    ```

3.  **Install dependencies:**
    ```bash
    pip install -e .
    ```

### Running the Application

```bash
chainlit run app.py
```

### Running the Mock API Server

To start the mock API server, run the following command:

```bash
python mock-api.py
```

The API will be available at `http://0.0.0.0:8001`.


## Database

To populate the database with mock data, run the following command:

```bash
python -m scripts.populate_sqllight_db
```

## Docker

To start the PostgreSQL and pgAdmin services, run the following command:

```bash
docker compose up -d
```

## Prefect

To deploy and run the test flow, run the following commands:

```bash
prefect server start &
python flows/test.py
```

You can view the flow run in the Prefect UI at http://127.0.0.1:4200.

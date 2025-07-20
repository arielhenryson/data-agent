# NLtSQL

This is a Python application that translates natural language to SQL queries.

## Setup

### Conda Environment

1.  **Create a new conda environment:**
    ```bash
    conda create --name nltsql python=3.11
    ```

2.  **Activate the environment:**
    ```bash
    conda activate nltsql
    ```

3.  **Install uv:**
    ```bash
    pip install uv
    ```

4.  **Install dependencies:**
    ```bash
    uv pip install -e .
    ```

### Running the Application

```bash
chainlit run app.py
```

## Database

To populate the database with mock data, run the following command:

```bash
python -m scripts.populate_db
```

## Docker

To start the PostgreSQL and pgAdmin services, run the following command:

```bash
docker-compose up -d
```

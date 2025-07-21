from prefect import task, flow

@task
def extract_data():
    # Code to get data from a source
    return [1, 2, 3]

@task
def transform_data(data):
    # Code to modify the data
    return [x * 10 for x in data]

@task
def load_data(transformed_data):
    # Code to load the data into a destination
    print(f"Loading data: {transformed_data}")

@flow
def my_etl_flow():
    data = extract_data()
    transformed = transform_data(data)
    load_data(transformed)
from google.cloud import bigquery
import os

# Point at your service account key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Pranav\Documents\CS_Python\nyc-taxi-pipeline\nyc-taxi-501018-bb4e786d0865.json"

PROJECT_ID = "520469854189"
client = bigquery.Client(project=PROJECT_ID)

table_id = f"{PROJECT_ID}.raw.yellow_tripdata"

job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.PARQUET,
    write_disposition="WRITE_TRUNCATE",  # replace table if it exists
)

with open("raw/yellow_tripdata_2026-01.parquet", "rb") as f:
    job = client.load_table_from_file(f, table_id, job_config=job_config)

job.result()  # wait for completion

table = client.get_table(table_id)
print(f"Loaded {table.num_rows:,} rows into {table_id}")
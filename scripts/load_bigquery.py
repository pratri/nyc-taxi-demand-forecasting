from google.cloud import bigquery

# Auth uses the GOOGLE_APPLICATION_CREDENTIALS env var pointing at a
# service-account key. Set it before running, e.g. in PowerShell:
#   $env:GOOGLE_APPLICATION_CREDENTIALS = "path\to\key.json"
PROJECT_ID = "nyc-taxi-501018"
client = bigquery.Client(project=PROJECT_ID)

table_id = f"{PROJECT_ID}.raw.yellow_tripdata"

job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.PARQUET,
    write_disposition="WRITE_TRUNCATE",  # replace table if it exists
)

with open("raw/yellow_tripdata_2025-01.parquet", "rb") as f:
    job = client.load_table_from_file(f, table_id, job_config=job_config)

job.result()  # wait for completion

table = client.get_table(table_id)
print(f"Loaded {table.num_rows:,} rows into {table_id}")

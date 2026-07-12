from google.cloud import bigquery
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Pranav\Documents\CS_Python\nyc-taxi-pipeline\nyc-taxi-501018-bb4e786d0865.json"

PROJECT_ID = "520469854189"
client = bigquery.Client(project=PROJECT_ID)

table_id = f"{PROJECT_ID}.raw.taxi_zones"

job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    autodetect=True,
    write_disposition="WRITE_TRUNCATE",
)

with open("raw/taxi_zone_lookup.csv", "rb") as f:
    job = client.load_table_from_file(f, table_id, job_config=job_config)

job.result()
table = client.get_table(table_id)
print(f"Loaded {table.num_rows} rows into {table_id}")
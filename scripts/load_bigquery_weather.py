from google.cloud import bigquery

# Auth uses the GOOGLE_APPLICATION_CREDENTIALS env var (see load_bigquery.py).
PROJECT_ID = "nyc-taxi-501018"
client = bigquery.Client(project=PROJECT_ID)

table_id = f"{PROJECT_ID}.raw.weather_central_park"

job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    autodetect=True,
    write_disposition="WRITE_TRUNCATE",
)

with open("raw/weather_central_park_2025.csv", "rb") as f:
    job = client.load_table_from_file(f, table_id, job_config=job_config)

job.result()
table = client.get_table(table_id)
print(f"Loaded {table.num_rows} rows into {table_id}")
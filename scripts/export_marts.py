import duckdb

src = duckdb.connect("taxi.duckdb")
src.execute("ATTACH 'reports/sources/taxi/marts.duckdb' AS slim;")

for mart in ["mart_earnings_by_zone_hour", "mart_earnings_by_weather", "mart_daily_earnings"]:
    src.execute(f"CREATE OR REPLACE TABLE slim.{mart} AS SELECT * FROM main.{mart};")
    count = src.execute(f"SELECT count(*) FROM slim.{mart}").fetchone()[0]
    print(f"Copied {mart}: {count:,} rows")

src.close()
print("Wrote reports/sources/taxi/marts.duckdb")
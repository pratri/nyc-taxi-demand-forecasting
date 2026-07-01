import duckdb
con = duckdb.connect("taxi.duckdb")

# Find a colliding key, then show the full rows behind it
con.sql("""
    WITH dupes AS (
        SELECT trip_id
        FROM main.stg_yellow_trips
        GROUP BY trip_id
        HAVING count(*) > 1
        LIMIT 1
    )
    SELECT s.*
    FROM main.stg_yellow_trips s
    JOIN dupes USING (trip_id)
""").show()

con.close()
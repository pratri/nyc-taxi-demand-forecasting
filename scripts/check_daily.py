import duckdb
con = duckdb.connect("taxi.duckdb")

print("Row count (should be ~365):")
con.sql("SELECT count(*) AS days FROM main.mart_daily_earnings").show()

print("First few days:")
con.sql("""
    SELECT trip_date, round(earnings_per_hour,2) AS eph, trip_count,
           temp_max_f, precip_in, snowfall_in, day_of_week
    FROM main.mart_daily_earnings
    ORDER BY trip_date
    LIMIT 8
""").show()

print("Sanity: range of daily eph (watch for absurd values):")
con.sql("""
    SELECT round(min(earnings_per_hour),2) AS min_eph,
           round(avg(earnings_per_hour),2) AS avg_eph,
           round(max(earnings_per_hour),2) AS max_eph
    FROM main.mart_daily_earnings
""").show()

con.close()
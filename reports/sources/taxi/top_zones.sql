select pickup_location_id, pickup_hour, pickup_dow, trip_count,
       round(earnings_per_hour, 2) as eph
from main.mart_earnings_by_zone_hour
where trip_count > 50
order by eph desc
limit 25
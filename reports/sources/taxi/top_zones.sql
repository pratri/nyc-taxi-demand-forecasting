select
    zone_name,
    borough,
    cast(pickup_hour as integer)  as pickup_hour,
    cast(pickup_dow as integer)   as pickup_dow,
    cast(trip_count as integer)   as trip_count,
    round(earnings_per_hour, 2)   as eph
from main.mart_earnings_by_zone_hour
where trip_count > 500
  and earnings_per_hour is not null
order by eph desc
limit 15
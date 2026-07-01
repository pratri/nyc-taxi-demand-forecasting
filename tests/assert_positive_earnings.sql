-- Fails if any valid trip earned nothing or less.
select *
from {{ ref('int_trips_valid') }}
where driver_earnings <= 0
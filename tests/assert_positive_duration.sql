-- Fails if any valid trip has non-positive duration.
-- A test returns the OFFENDING rows; zero rows = pass.
select *
from {{ ref('int_trips_valid') }}
where dropoff_at <= pickup_at
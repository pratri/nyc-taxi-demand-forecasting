-- Fails if more than 50 trips are missing weather (allows a few month-boundary stragglers).
select count(*) as missing
from {{ ref('int_trips_weather') }}
where temp_max_f is null
having count(*) > 50
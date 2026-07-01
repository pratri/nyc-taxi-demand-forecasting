with trips as (
    select * from {{ ref('int_trips_weather') }}
),

categorized as (
    select
        driver_earnings,
        trip_duration_min,
        case
            when snowfall_in > 0 then 'snow'
            when precip_in >= 0.1 then 'rain'
            when precip_in > 0    then 'light rain'
            else 'dry'
        end as weather_condition,
        case
            when temp_max_f < 32 then 'freezing'
            when temp_max_f < 45 then 'cold'
            else 'mild'
        end as temp_band
    from trips
    where temp_max_f is not null   -- drop the 6 unmatched trips
),

by_condition as (
    select
        weather_condition,
        count(*)                                   as trip_count,
        sum(driver_earnings)                       as total_earnings,
        sum(trip_duration_min) / 60.0              as total_hours,
        sum(driver_earnings)
            / nullif(sum(trip_duration_min) / 60.0, 0) as earnings_per_hour,
        avg(driver_earnings)                       as avg_earnings_per_trip
    from categorized
    group by weather_condition
)

select * from by_condition
order by earnings_per_hour desc
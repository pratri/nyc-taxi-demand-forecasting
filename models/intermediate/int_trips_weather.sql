with trips as (
    select * from {{ ref('int_trips_valid') }}
),

weather as (
    select * from {{ ref('stg_weather') }}
),

joined as (
    select
        trips.*,
        weather.precip_in,
        weather.snowfall_in,
        weather.snow_depth_in,
        weather.temp_max_f,
        weather.temp_min_f
    from trips
    left join weather
        on cast(trips.pickup_at as date) = weather.weather_date
)

select * from joined
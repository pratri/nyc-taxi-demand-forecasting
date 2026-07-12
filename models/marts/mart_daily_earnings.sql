with trips as (
    select * from {{ ref('int_trips_weather') }}
),

daily as (
    select
        cast(pickup_at as date)                     as trip_date,
        sum(driver_earnings)                        as total_earnings,
        sum(trip_duration_min) / 60.0               as total_hours,
        count(*)                                    as trip_count,
        sum(driver_earnings)
            / nullif(sum(trip_duration_min) / 60.0, 0) as earnings_per_hour,
        -- weather is identical across all trips on a day, so max() just picks that day's value
        max(temp_max_f)                             as temp_max_f,
        max(temp_min_f)                             as temp_min_f,
        max(precip_in)                              as precip_in,
        max(snowfall_in)                            as snowfall_in,
        max(snow_depth_in)                          as snow_depth_in
    from trips
    where temp_max_f is not null
    group by cast(pickup_at as date)
),

featured as (
    select
        *,
        extract(dow from trip_date)                 as day_of_week,
        extract(month from trip_date)               as month,
        case when extract(dow from trip_date) in (0, 6) then 1 else 0 end as is_weekend
    from daily
)

select * from featured
order by trip_date
with trips as (
    select * from {{ ref('int_trips_valid') }}
),

zones as (
    select * from {{ ref('stg_zones') }}
),

enriched as (
    select
        pickup_location_id,
        extract(hour from pickup_at) as pickup_hour,
        {% if target.name == 'dev' %}
        extract(dow from pickup_at) as pickup_dow,
        {% else %}
        extract(dayofweek from pickup_at) as pickup_dow,
        {% endif %}
        driver_earnings,
        trip_duration_min
    from trips
),

aggregated as (
    select
        pickup_location_id,
        pickup_hour,
        pickup_dow,
        count(*)                              as trip_count,
        sum(driver_earnings)                  as total_earnings,
        sum(trip_duration_min) / 60.0         as total_hours,
        sum(driver_earnings)
            / nullif(sum(trip_duration_min) / 60.0, 0) as earnings_per_hour
    from enriched
    group by pickup_location_id, pickup_hour, pickup_dow
),

named as (
    select
        a.pickup_location_id,
        z.zone_name,
        z.borough,
        a.pickup_hour,
        a.pickup_dow,
        a.trip_count,
        a.total_earnings,
        a.total_hours,
        a.earnings_per_hour
    from aggregated a
    left join zones z
        on a.pickup_location_id = z.zone_id
)

select * from named
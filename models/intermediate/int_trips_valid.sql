with trips as (
    select * from {{ ref('stg_yellow_trips') }}
),

valid as (
    select
        pickup_at,
        dropoff_at,
        pickup_location_id,
        dropoff_location_id,
        {{ dbt.datediff('pickup_at', 'dropoff_at', 'minute') }} as trip_duration_min,
        fare_amount,
        tip_amount,
        extra,
        fare_amount + tip_amount + extra as driver_earnings
    from trips
    where
        {{ dbt.datediff('pickup_at', 'dropoff_at', 'minute') }} >= 1
        and (fare_amount + tip_amount + extra) > 0
        and pickup_location_id not in (264, 265)
)

select * from valid
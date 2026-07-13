{{
    config(
        materialized='incremental' if target.type == 'duckdb' else 'table',
        unique_key='trip_id'
    )
}}
with source as (
    select * from {{ source('raw', 'yellow_tripdata') }}
),

renamed as (
    select
        {{ dbt_utils.generate_surrogate_key([
            'VendorID',
            'tpep_pickup_datetime',
            'tpep_dropoff_datetime',
            'PULocationID',
            'DOLocationID',
            'fare_amount',
            'tip_amount',
            'trip_distance',
            'total_amount'
        ]) }} as trip_id,
        VendorID              as vendor_id,
        tpep_pickup_datetime  as pickup_at,
        tpep_dropoff_datetime as dropoff_at,
        PULocationID          as pickup_location_id,
        DOLocationID          as dropoff_location_id,
        passenger_count,
        trip_distance,
        payment_type,
        fare_amount,
        tip_amount,
        extra,
        total_amount
    from source

    {% if is_incremental() %}
    where tpep_pickup_datetime > (select max(pickup_at) from {{ this }})
    {% endif %}
),

deduped as (
    select *,
        row_number() over (
            partition by trip_id
            order by pickup_at
        ) as _row_num
    from renamed
)

select
    {% if target.type == 'duckdb' %}
    * exclude (_row_num)
    {% else %}
    * except (_row_num)
    {% endif %}
from deduped
where _row_num = 1
with source as (
    select * from {{ source('raw', 'weather_central_park') }}
),

renamed as (
    select
        cast(DATE as date)  as weather_date,
        PRCP                as precip_in,
        SNOW                as snowfall_in,
        SNWD                as snow_depth_in,
        TMAX                as temp_max_f,
        TMIN                as temp_min_f
    from source
)

select * from renamed
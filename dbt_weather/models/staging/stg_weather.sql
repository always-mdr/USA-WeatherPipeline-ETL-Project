with source as (
    -- In duckdb, we can query external locations directly if configured or just use the macro.
    -- dbt-duckdb handles external_location gracefully.
    select * from {{ source('iceberg_warehouse', 'weather_historical') }}
),
renamed as (
    select
        -- date comes in as timestamp, cast to date
        cast(date as date) as measurement_date,
        city as city_name,
        temp_max_c,
        temp_min_c,
        precipitation_mm,
        wind_speed_max_kmh
    from source
    -- filter out null rows just in case
    where city is not null
)
select * from renamed

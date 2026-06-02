with staging as (
    select * from {{ ref('stg_weather') }}
),
monthly_agg as (
    select
        city_name,
        date_trunc('month', measurement_date) as month,
        avg(temp_max_c) as avg_temp_max_c,
        avg(temp_min_c) as avg_temp_min_c,
        sum(precipitation_mm) as total_precipitation_mm,
        max(wind_speed_max_kmh) as max_wind_speed_kmh
    from staging
    group by 1, 2
)
select
    city_name,
    month,
    avg_temp_max_c,
    avg_temp_min_c,
    total_precipitation_mm,
    max_wind_speed_kmh
from monthly_agg
order by city_name, month

{{
    config(
        materialized='incremental',
        partition_by={
            "field": "Release_Date",
            "data_type": "date",
            "granularity": "year"
        }
    )
}}

SELECT
    Name,
    Platform,
    Genre,
    Publisher,
    NA_Sales,
    EU_Sales,
    JP_Sales,
    Other_Sales,
    Global_Sales,
    CAST(Date AS DATE) AS Release_Date,
    Refunds
FROM {{ source('external','raw_videogame_table') }}

{%- if is_incremental() %}
  -- this filter will only be applied on an incremental run
    WHERE dt = '{{ var("day") }}'

{%- else %}
    WHERE dt = "2024-03-18"

{% endif %}
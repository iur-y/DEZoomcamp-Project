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
WHERE Publisher IS NOT NULL

{%- if is_incremental() %}
  -- this filter will only be applied on an incremental run
    AND dt = '{{ env_var("EXECUTION_DAY") }}'

{%- else %}
  -- the `if` above fails if the table doesn't already exist, doesn't matter
  -- for our artificial case, we still just filter data based on today
    AND dt = '{{ env_var("EXECUTION_DAY") }}'

{% endif %}

{{
    config(materialized='incremental')
}}

SELECT *
FROM {{ source('staging','raw_videogame_table') }}

{%- if is_incremental() %}
  -- this filter will only be applied on an incremental run
    WHERE dt = '{{ var("day") }}'

{%- else %}
    WHERE dt = "2024-03-18"

{% endif %}
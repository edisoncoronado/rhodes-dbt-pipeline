{{ config(materialized='view') }}
select *
from {{ source('raw', 'REGIONAL_MANAGER_LOOKUP') }}
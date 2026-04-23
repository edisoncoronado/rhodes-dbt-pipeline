select distinct s.region
from {{ ref('stg_homebuilder_sales') }} s
left join {{ ref('stg_regional_manager_lookup') }} r
    on s.region = r.region
where r.region is null
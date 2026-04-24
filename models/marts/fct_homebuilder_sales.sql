select
    CONTRACT_ID,
	COMMUNITY,
	CITY,
	s.REGION,
	PLAN_NAME,
	SQFT,
	BEDROOMS,
	BATHROOMS,
	BASE_PRICE,
	UPGRADE_AMOUNT,
	INCENTIVE_AMOUNT,
	CONTRACT_PRICE,
	CONTRACT_DATE,
	CLOSE_DATE,
	DAYS_TO_CLOSE,
    datediff('day', s.contract_date, s.close_date) as days_to_close_cal,

    case
        when s.sqft > 0 then s.contract_price / s.sqft
        else null
    end as price_per_square_foot,

    case
        when upper(trim(STATUS)) =  'CANCELED' then 1
        else 0
    end as cancellation_flag,
    case
        when upper(trim(STATUS)) =  'CLOSED' and CONTRACT_PRICE > 0 then 1
        else 0
    end as sold_flag,
    case
        when upper(trim(STATUS)) =  'UNDER CONTRACT' then 1
        else 0
    end as under_contract_flag,
	STATUS,
	BUYER_SOURCE,
	AGENT_COMMISSION,
	LOAN_TYPE,
	SALES_CONSULTANT,
	REGIONAL_MANAGER,
	SALES_TARGET_UNITS,
	MARGIN_TARGET_PCT
from {{ ref('stg_homebuilder_sales') }} s
left join {{ ref('stg_regional_manager_lookup') }} r
    on s.region = r.region
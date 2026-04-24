{{ config( materialized='view') }}
select
	CONTRACT_ID,
	COMMUNITY,
	CITY,
	REGION,
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
	case
    when upper(trim(STATUS)) in ('CANCELLED', 'CANCELED') then 'CANCELED'
    else upper(trim(STATUS))
    end as STATUS,
	BUYER_SOURCE,
	AGENT_COMMISSION,
	LOAN_TYPE,
	SALES_CONSULTANT
from {{ source('raw', 'HOMEBUILDER_SALES') }} 
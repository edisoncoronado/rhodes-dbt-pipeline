select region, count(*) as sales_count
from RHODES_DWH.ANALYTICS.FCT_HOMEBUILDER_SALES
group by region
order by sales_count desc;

select status, count(*) as total
from RHODES_DWH.ANALYTICS.FCT_HOMEBUILDER_SALES
group by status
order by total;

select regional_manager, avg(price_per_square_foot) as avg_price_psf
from RHODES_DWH.ANALYTICS.FCT_HOMEBUILDER_SALES
group by regional_manager
order by avg_price_psf desc;

select * from RHODES_DWH.ANALYTICS.FCT_HOMEBUILDER_SALES


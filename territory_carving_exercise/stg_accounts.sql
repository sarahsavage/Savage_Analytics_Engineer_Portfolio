{{
    config(
        materialized = "view"
    )
}}

with accounts_all as (select * from {{ source("SALESFORCE", "ACCOUNTS") }})

select
  account_id,
  company_name,
  country,
  region,
  state,
  industry,
  employee_count,
  annual_revenue,
  zip,
  geography,
  closest_airport
--assuming we have lat/long and airport data available
--likely in a real-world scenario, this would not be in the raw accounts table but could be enriched from another source
from accounts_all
where is_active = true
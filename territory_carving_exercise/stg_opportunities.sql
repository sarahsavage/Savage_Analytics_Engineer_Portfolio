{{
    config(
        materialized = "view"
    )
}}

with opportunities_all as (select * from {{ source("SALESFORCE", "OPPORTUNITIES") }})


select
  opportunity_id,
  account_id,
  stage,
  amount,
  rating,
  predictive_score,
  --making an assumption that we have this somewhere in a model
  --if no predictive score is currently available, bring in Data Science
  date(created_at) as opportunity_created_date,
  date(most_recent_touchpoint) as most_recent_touchpoint
from opportunities_all
where stage not in ('Closed Lost', 'Disqualified')
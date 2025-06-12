{{
    config(
        materialized = "table"
    )
}}

with opportunities as (select * from {{ ref(stg_opportunities) }}),
     accounts as (select * from {{ ref(stg_accounts) }})

select
  acc.account_id,
  acc.region,
  acc.state,
  acc.industry,
  acc.employee_count,
  acc.annual_revenue,
  max(opp.most_recent_touchpoint) as most_recent_touchpint,
  datediff(current_date, max(opp.opportunity_created_date) as days_since_last_opportunity,
  count(opp.opportunity_id) AS open_opportunity_count,
  sum(opp.amount) AS potential_revenue,
  avg(case when opp.rating = 'Hot' then 3
           when opp.rating = 'Warm' then 2
           when opp.rating = 'Cold' then 1
      else 0 end) as avg_opportunity_rating,
  avg(opp.predictive_score) AS avg_predictive_score,
  -- weighted account score
  coalesce(employee_count,0) *0.05 +
  coalsesce(annual_revenue,0) *0.00005 +
  sum(opp.amount)*0.001 +
  avg(opp.predictive_score) *0.5 +
  avg(case when opp.rating = 'Hot' then 3
           when opp.rating = 'Warm' then 2
           when opp.rating = 'Cold' then 1
      else 0 end) *5 +
  (case when max(opp.created_date) is null then 0
        else greatest(0, least(30, 30 - days_since_last_opportunity) end) * 0.5
--prevents negative numbers
  as account_score
from accounts as acc
left join opportunities as opp
    on acc.account_id = opp.account_id
group by 1,2,3,4,5,6

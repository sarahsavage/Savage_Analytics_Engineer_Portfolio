{{
    config(
        materialized = "table"
    )
}}

with account_scores as (select * from {{ ref(int_account_scoring) }}),
     sales_reps as (select * from {{ ref(stg_sales_reps) }}),
--assuming this would exist but I didn't create one for this exercise

rep_capacity as (
  select
    rep_id,
    region,
    max(account_score) * 10 as max_capacity
--placeholder, to be re-evaluated based on stakeholder input
  from sales_reps
),

scored_accounts as (
  select *, row_number() over (order by account_score desc) as account_priority
  from account_scores
),

rep_allocation as (
  select
    scored_accounts.account_id,
    sales_reps.rep_id,
    scored_accounts.account_score,
    sum(scored_accounts.account_score) over (partition by sales_rep.rep_id order by scored_accounts.account_priority) as cumulative_score
  from scored_accounts
  join sales_reps
  on scored.accounts.region = sales_reps.region
  )

select *
from rep_allocation
where cumulative_score <= (select max_capacity from rep_capacity where rep_id = rep_allocation.rep_id)

--there will likely be some unassigned accounts, those may need to be assigned manually, or the model re-evaluated, or makes a case for hiring more reps?
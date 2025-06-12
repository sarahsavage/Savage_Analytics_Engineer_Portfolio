{{
    config(
        materialized = "view"
    )
}}

with territories as (select * from {{ ref(territory_assignments) }}),
     accounts as (select * from {{ ref(stg_saccounts) }}),

assigned_accounts as (
  select account_id
  from territories
),

all_accounts as (
  select account_id from accounts
)

select
    all_accounts.account_id
from all_accounts
left join assigned_accounts
on all_accounts.account_id = assigned_accounts.account_id

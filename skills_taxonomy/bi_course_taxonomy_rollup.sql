{{
    config(
        materialized="table"
    )
}}

with courserun            as (select * from /* {{ cref('*/dim_courseruns/*') }} */ )
   , courseskill          as (select * from /* {{ cref('*/fact_course_skill/*') }} */ )
   , taxonomy             as (select * from /* {{ cref('*/dim_skill_taxonomy/*') }} */ )
   , content              as (select * from /* {{ cref('*/bi_course_content_daily_rollup/*') }} */)
   , cnds                 as (select * from /* {{ cref('*/fact_course_availability_rollup_daily/*') }} */)
   , prog_courserun       as (select * from /* {{ cref('*/core_courserun_active_program_membership/*') }} */)
   , languages            as (
    select course_key
         , coalesce(max(language), 'missing') as language
    from courserun
    group by course_key
)
   , program_course       as (
    select course_id
         , listagg(distinct program_type, ' | ') within group ( order by program_type )   as combined_program_type
         , listagg(distinct program_title, ' | ') within group ( order by program_title ) as combined_program_title
         --listagg for program ensures that courses associated with multiple programs will only be listed once, in the combined_program_type
    from prog_courserun
    group by course_id
)
   , taxonomy_with_course as
    (
        select cs.course_key
             , tax.skill_id
             , tax.skill_name
             , tax.skill_type
             , tax.skill_created
             , tax.skill_modified
             , cs.course_match_confidence
             , listagg(distinct tax.skill_name, ' | ') within group ( order by tax.skill_name )
            --listagg for skill, subcategory, and category are specifically for ease of tableau reporting, allowing for a view with only one row per course
                       over (partition by cs.course_key)                            as all_tagged_skills
             , count(distinct tax.skill_id) over (partition by cs.course_key)       as count_tagged_skills
             , tax.subcategory_id
             , tax.subcategory_name
             , tax.subcategory_created
             , tax.subcategory_modified
             , listagg(distinct tax.subcategory_name, ' | ') within group ( order by tax.subcategory_name )
                       over (partition by cs.course_key)                            as all_tagged_subcategories
             , count(distinct tax.subcategory_id) over (partition by cs.course_key) as count_tagged_subcategories
             , tax.category_id
             , tax.category_name
             , tax.category_created
             , tax.category_modified
             , listagg(distinct tax.category_name, ' | ') within group ( order by tax.category_name )
                       over (partition by cs.course_key)                            as all_tagged_categories
             , count(distinct tax.category_id) over (partition by cs.course_key)    as count_tagged_categories
        from taxonomy         as tax
             join courseskill as cs
                  on tax.skill_id = cs.skill_id
    )
   , course_metadata      as (
    select cnds.course_key
         , cnds.course_number_id as course_id
         , cnds.is_upcoming      as is_upcoming
         , cnds.is_active        as is_active
         , cnds.is_archived      as is_archived
         , case when cnds.is_upcoming = 1 then 'Upcoming'
                when cnds.is_active = 1 then 'Active'
                when cnds.is_archived = 1 then 'Archived'
                else 'Error' end as current_availability_type
    from cnds
         --we're tracking the current availability status so the the team can clearly identify skills gaps as they pertain to current availability
    where cnds.event_date = current_date()
)
select content.course_key
     , twc.skill_id
     , twc.skill_name
     , twc.skill_type
     , twc.skill_created
     , twc.skill_modified
     , twc.course_match_confidence
     , twc.all_tagged_skills
     , twc.subcategory_id
     , twc.subcategory_name
     , twc.subcategory_created
     , twc.subcategory_modified
     , twc.all_tagged_subcategories
     , twc.category_id
     , twc.category_name
     , twc.category_created
     , twc.category_modified
     , twc.all_tagged_categories
     , content.event_date
     , content.in_learning_window
     , content.in_revenue_window
     , content.partner
     , content.program_id
     , content.daily_b2c_revenue
     , content.daily_b2b_revenue
     , content.enrollments
     , content.b2c_enrollments
     , content.b2c_paid_enrollments
     , content.courseruns_started
     , content.users_passed
     , content.users_certified
     , course_metadata.current_availability_type
     , coalesce(program.combined_program_type, 'Non-Program')  as combined_program_type
     , coalesce(program.combined_program_title, 'Non-Program') as combined_program_title
     , languages.language
from taxonomy_with_course     as twc
     join      content
               on content.course_key = twc.course_key
     join      course_metadata
               on twc.course_key = course_metadata.course_key
     join      languages
               on languages.course_key = twc.course_key
     left join program_course as program
               on program.course_id = course_metadata.course_id
--final output of this table will result in multiple rows per course, one for each skill associated with the course
--because metrics such as revenue, enrollments, certificates, etc. are calculated per course not per skill/subcategory/category, summing CANNOT be done across multiple skills
--this duplication of metrics is deliberate and necessary to sort courses by taxonomy levels and evaluate those skills/subcategories/categories by the desired metrics
--use this table with caution

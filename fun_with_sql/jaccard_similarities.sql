--this code compares the overlap of skills taught in courses to the skills needed for various jobs for the career progression experiment
--if this idea is warranted for full production, we may want to have some intermediate models created

with jobs_list       as
    (
        select distinct
               case when job_title in
                         ('Data Scientist', 'Manager/Data Scientist', 'Data Analyst', 'Machine Learning Engineer', 'Data Science Manager',
                          'Data Engineer', 'Lead Data Scientist', 'Analytics Manager', 'Research Scientist', 'Data Analytics Scientist',
                          'Director of Data Science') then 'Data Scientist'
                    when job_title in
                         ('Product Owner', 'Program Manager', 'Marketing Product Manager', 'Business Analyst', 'Digital Product Manager',
                          'Business Systems Analyst', 'Project Manager', 'Director of Product Management', 'Account Executive',
                          'Technical Program Manager', 'Product Manager') then 'Product Manager'
                    when job_title in
                         ('Software Engineer', 'Full Stack Developer', 'Lead Software Engineer', 'Application Developer',
                          'Software Engineering Intern',
                          '.NET Developer', 'Java Developer', 'Principal Software Engineer', 'Full Stack Software Engineer',
                          'Software Development Engineer', 'Software Developer') then 'Software Engineer' end
                                                     as career_track
               --these are the ones chosen for the initial experiment.
               --If the experiment is successful, we will need a way to automate the career track groupings/labels
             , job_title                             as name
--generic 'name' of column name makes for a simpler union which is needed for the jaccard similarity
             , listagg(distinct skill_name, ' , ') within group (order by skill_name)
                       over (partition by job_title) as all_tagged_skills
        from prod.core.dim_job_skill
        where career_track is not null
        --limiting it to only these jobs for now
    )

   , course_skill    as
    (
        select distinct
               course_key                             as name
--same generic column name for union
             , listagg(distinct skill, ' , ') within group (order by skill)
                       over (partition by course_key) as all_tagged_skills
        from prod.core.fact_job_taxonomy_course_map
    )

   , combined_tables as
    (
        select name
             , all_tagged_skills
        from jobs_list
        union all
        select name
             , all_tagged_skills
        from course_skill
--this combines all jobs and course_keys into one column and the comma separated list of skills for each into another
    )

   , jaccard_set     as
    (
        select name
             , split(all_tagged_skills, ',') as skill
        from combined_tables
        --splitting into individual skills allows for the jaccard formula to be correctly applied
    )
   , jaccard_stage   as
    (
        select jac_a.name                                               as name_1
             , jac_b.name                                               as name_2
             , array_size(jac_a.skill)                                  as skill_count_1
             , array_size(jac_b.skill)                                  as skill_count_2
             , array_size(array_intersection(jac_a.skill, jac_b.skill)) as intersection_count
        from jaccard_set      as jac_a
             join jaccard_set as jac_b
                  on jac_a.name < jac_b.name
--self join allows all skills from each course_key/job to be compared to one another to find the intersection
    )

select career_track
--including career track allows for separation into job categories
     , name_1                                                                    as job_title
     , name_2                                                                    as course_key
     , intersection_count
--how many skills each has in common
     , skill_count_1 + skill_count_2                                             as union_count
--how many total skills between the two
     , intersection_count / (skill_count_1 + skill_count_2 - intersection_count) as jaccard_score
--jaccard score is based on the overlap divided by the difference
from jaccard_stage
     join jobs_list
          on name = name_1
--this filters out courses being compared to courses, though this is something we may want to do in the future
     join prod.core.dim_courses
          on name_2 = course_key
--this filters out jobs being compared to other jobs, though this is also something we may want to do in the future
where intersection_count > 0
--want to make sure there is at least one overlapping skill, we may want to make this threshold  higher for the experiment
  and name_1 <> name_2
--keeps courses/jobs from being compared to themselves
order by career_track
       , job_title
       , jaccard_score desc
--this produces a list of job titles and courses that have at least one overlapping skill, along with the jaccard score
--additional course metadata can be joined to this list to determine the 'best' courses to include in the experiment
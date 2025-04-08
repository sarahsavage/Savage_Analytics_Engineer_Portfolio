Jaccard Similarity is a metric used to measure the similarity between two sets. 
It is defined as the ratio of the size of the intersection of the two sets to the size of their union.

Full disclosure, it's probably easier to do in Python but I wanted to see if I could do it in SQL
because I work extensively in DBT and Python models in DBT are not quite as functional as I'd like them to be.

The premise of this project was that courses are tagged with specific skills, i.e. what skills are taught by each course. 
Skills taxonomy is from the Lightcast API: https://lightcast.io/open-skills. Lightcast also has database of skills tagged to 
jobs based on job titles in Linkedin/Indeed postings as well as public data provided by the government. Step one was to create 
a dataset with a few different career progressions based on title and median salary. Then, I created a data model using 
Jaccard similarity to match up courses with relevant jobs based on similarity.

The final state of this project would be to create a recommender engine so that a user can search for a specific
job title or career path and see what courses will best prepare them for that job. A future iteration might be to 
allow users to create a portfolio of skills they already have and skills learned from successful completion of courses
and then run a gap analysis between their current skillset and what is required in a particular job, to recommend
learning to bridge the gap.

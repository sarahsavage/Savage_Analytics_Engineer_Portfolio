#!/usr/bin/env python
# coding: utf-8

# In[1]:


import matplotlib as mpl
import matplotlib.pyplot as plt 
get_ipython().run_line_magic('matplotlib', 'inline')
import seaborn as sns
import pandas as pd
import statsmodels.api as sm
sns.set_style("darkgrid")
mpl.rcParams['figure.figsize'] = (20,5)


# In[2]:


bechdel_only = pd.read_csv('Bechdel Complete.csv')
print('Bechdel Only')
print(bechdel_only.head())
print(bechdel_only.info())
bechdel_imdb = pd.read_csv('Bechdel plus IMDB.csv')
print('Bechdel with IMDB Ratings')
print(bechdel_imdb.head())
print(bechdel_imdb.info())
bechdel_imdb_budget = pd.read_csv('Bechdel with IMDB and Budget.csv')
print('Bechdel with Ratings and Budget')
print(bechdel_imdb_budget.head())
print(bechdel_imdb_budget.info())


# <b>Background:</b>
# <p>The Bechdel Test is a way of evaluating movies for inclusion of women. It was popularized by comic book writer Alison Bechdel in 1985. In order for a film to pass the Bechdel Test, it must fulfill 3 criteria:</p>
# <ol type=1>
#     <li>It must have at least two named female characters.</li>
#     <li>Those characters must have at least one conversation with each other.</li>
#     <li>The conversation must be about something other than a man.</li></ol>
# 
# <p>It was originally proposed as a way to show just how few popular movies actually pass this very low bar. Though it is woefully inadequate in some ways and better tests of inclusion and diversity are needed, the popularity and widespread use, as well as the simplicity of the test, mean that there is fairly comprehensive data on movies that pass or fail. The data here was taken from bechdel.com, which has a database of over 8000 films with their imdb ids and a pass/fail on each of the three criteria.</p>
#     
#     
#     

# In[3]:


pass_rate = bechdel_only['bechdel_test'].value_counts(normalize=True)
print(pass_rate)

labels = 'PASS', 'FAIL'
explode = (0, 0.1)
colors = ['limegreen', 'orangered']
plt.pie(pass_rate, labels = labels, autopct='%1.1f%%', startangle= 15, shadow = True, colors= colors, explode=explode)
plt.axis('equal')
plt.title('Percent of Total Films Passing or Failing Bechdel Test')
plt.show()


# Overall, 58% of the movies in the database pass the Bechdel Test, while 42% fail. These seem like positive numbers! However, when you consider how low the bar is, we'd like that number to be much, much higher. In fact, considering how easy it should be to pass, theoretically, we should be aiming for 100% of films made to pass the test. Additionally, it is important to keep in mind that this list comes from a moderated site (bechdeltest.com) based on user submissions, so there may be some bias towards watching and submitting movies more likely to pass the Bechdel Test.

# In[4]:


bechdel_fail = bechdel_only[bechdel_only["bechdel_test"] == "FAIL"]
pass_rate1 = bechdel_fail['2 named women'].value_counts(normalize=True)
labels = '2 or More Women', 'Fewer than 2 Women'
explode = (0, 0.1)
colors = ['limegreen', 'orangered']
plt.pie(pass_rate1, labels = labels, autopct='%1.1f%%', startangle= 15, shadow = True, colors= colors, explode=explode)
plt.axis('equal')
plt.title('Films Failing Test with Two Named Female Characters')
plt.show()


# Of the films failing the test, over 75% do have at least two named female characters. 

# In[5]:


pass_rate2 = bechdel_fail['talk to each other'].value_counts(normalize=True)
labels = 'Women Do Not Talk to Each Other', 'Women Talk to Each Other'
explode = (0, 0.1)
colors = ['orangered', 'limegreen']
plt.pie(pass_rate2, labels = labels, autopct='%1.1f%%', startangle= 15, shadow = True, colors= colors, explode=explode)
plt.axis('equal')
plt.title('Films Failing Test where Women Talk to Each Other')
plt.show()


# Criteria #2: Those women talk to each other, has a much lower pass rate. Relegated to two dimensional wives, girlfriends, and crushes, female characters in movies are often not allowed rich, complex lives, nor to they further the plot. They are seen primarily as accessories to the central male character(s).

# Next, we'll look at whether the percentage of movies passing the test is going up or down over time.

# In[6]:


bechdel_time = bechdel_only.groupby(['year', 'bechdel_test']).bechdel_test.count() 
bechdel_time = bechdel_time.unstack(level='bechdel_test')
bechdel_time.plot(color=('red', 'green'))
plt.show()


# In[7]:


nineties_forward = bechdel_only[bechdel_only['year']>=1990]
pass_rate_modern = nineties_forward['bechdel_test'].value_counts(normalize=True)
labels = 'PASS', 'FAIL'
explode = (0, 0.1)
colors = ['limegreen', 'orangered']
plt.pie(pass_rate_modern, labels = labels, autopct='%1.1f%%', startangle= 15, shadow = True, colors= colors, explode=explode)
plt.axis('equal')
plt.title('Percent of Total Films Passing or Failing Bechdel Test, 1990-2021')
plt.show()


# If we look at only movies from 1990 forward, the percentages get better, but still aren't anywhere close to 100% pass rate. 

# <b>Genres most Likely to Pass the Bechdel Test</b>

# In[8]:


bechdel_pass_imdb = bechdel_imdb[bechdel_imdb['bechdel_test'] == 'PASS']
genre1p = bechdel_pass_imdb.groupby(['genre1'])['bechdel_test'].count()
genre1p.plot(kind='bar', title='Bechdel Pass Rate by Primary Genre', ylabel='# of Passing Films',
         xlabel='Primary Genre', figsize=(15, 8), width=0.8)
plt.xticks(rotation=45)


# Based on primary listed genre, Comedy and Drama films are most likely to pass. Unfortunately, these do not map with the most popular in terms of ratings on IMDB. We'll see how these genres line up with box office success.

# In[9]:


bechdel_fail_imdb = bechdel_imdb[bechdel_imdb['bechdel_test'] == 'FAIL']
genre1f = bechdel_fail_imdb.groupby(['genre1'])['bechdel_test'].count()
genre1f.plot(kind='bar', title='Bechdel Fail Rate by Primary Genre', ylabel='# of Failing Films',
         xlabel='Primary Genre', figsize=(15, 8), width=0.8)
plt.xticks(rotation=45)


# Just as a secondary check, I ran the same chart for movies that fail the Bechdel Test. Here we see Action as the genre most likely to fail. Comedy and Drama are high here as well, which means there are just a lot of Comedy and Drama films made. No surprises there. Action films have 800 failing vs only 500 or so passing, while Comedy and Drama films have nearly double the amount passing vs. failing. Note to self: will want to make a stacked bar chart  here in Tableau. 

# In[10]:


bechdel_pass_imdb = bechdel_imdb[bechdel_imdb['bechdel_test'] == 'PASS']
genre2 = bechdel_pass_imdb.groupby(['genre2'])['bechdel_test'].count()
genre2.plot(kind='bar', title='Bechdel Pass Rate by Secondary Genre', ylabel='# of Passing Films',
         xlabel='Secondary Genre', figsize=(15, 8), width=0.8)
plt.xticks(rotation=45)


# Based on secondary genre, Drama is the clear winner, with Romance and Adventure also intriguing. 

# In[11]:


bechdel_pass_imdb = bechdel_imdb[bechdel_imdb['bechdel_test'] == 'PASS']
genre3 = bechdel_pass_imdb.groupby(['genre3'])['bechdel_test'].count()
genre3.plot(kind='bar', title='Bechdel Pass Rate by Tertiary Genre', ylabel='# of Passing Films',
         xlabel='Tertiary Genre', figsize=(15, 8), width=0.8)
plt.xticks(rotation=45)


# Based on tertirary genre, Romance and Thriller films have the highest number of passes. 

# <b>Directors Likely to Make Films Passing Bechdel Test</b>

# In[12]:


bechdel_pass_budget = bechdel_imdb_budget[bechdel_imdb_budget['bechdel_test'] == 'PASS']
bechdel_pass_director = bechdel_pass_budget[bechdel_pass_budget['year']>=1990]
director = bechdel_pass_director.groupby(['director'])['bechdel_test'].count().nlargest(20)
director.plot(kind='bar', title='Directors with Highest # Bechdel Pass, 1990 Forward', ylabel='# of Passing Films',
         xlabel='director', figsize=(15, 8), width=0.9)
plt.xticks(rotation=45)


# Top 20 directors in terms of # of films passing Bechdel test 1990 forward. Filtered for 1990 because we want to target directors who are still active and alive.

# In[13]:


bechdel_fail_budget = bechdel_imdb_budget[bechdel_imdb_budget['bechdel_test'] == 'FAIL']
bechdel_fail_director = bechdel_fail_budget[bechdel_fail_budget['year']>=1990]
directorf = bechdel_fail_director.groupby(['director'])['bechdel_test'].count().nlargest(20)
directorf.plot(kind='bar', title='Directors with Highest # Bechdel Fail, 1990 Forward', ylabel='# of Failing Films',
         xlabel='director', figsize=(15, 8), width=0.9)
plt.xticks(rotation=45)


# Running the director list again vs. movies that fail, I was pleased to see that there is actually not a lot of crossover. Some prolific directors will be likely to direct many that pass and many that fail, but there is a solid list of directors with higher numbers of passes than fails. These should be on our short list. 

# <b>Production Companies Likely to Make Films Passing Bechdel Test</b>

# In[14]:


bechdel_pass_prod = bechdel_pass_budget[bechdel_pass_budget['year']>=2000]
prod_com = bechdel_pass_prod.groupby(['production_company'])['bechdel_test'].count().nlargest(20)
prod_com.plot(kind='bar', title='Production Companies with Highest # Bechdel Pass', ylabel='# of Passing Films',
         xlabel='production company', figsize=(15, 8), width=0.9)
plt.xticks(rotation=45)


# Results filtered for year 2000 and forward so we can study companies making current films. 

# In[15]:


bechdel_fail_prod = bechdel_fail_budget[bechdel_fail_budget['year']>=2000]
prod_comf = bechdel_fail_prod.groupby(['production_company'])['bechdel_test'].count().nlargest(20)
prod_comf.plot(kind='bar', title='Production Companies with Highest # Bechdel Fail', ylabel='# of Failing Films',
         xlabel='production company', figsize=(15, 8), width=0.9)
plt.xticks(rotation=45)


# Though  many of the large production companies seem to have just as many films failing as passing, Dimension Films, Miramax, and Blumhouse Productions are all in the top 20 in regards to number of passing films but not in the top 20 for failing films. This is encouraging and these companies warrant a closer look. 

# <b>Writers Likely to Write Scripts that Pass the Bechdel Test</b>

# In[16]:


bechdel_pass_budget = bechdel_imdb_budget[bechdel_imdb_budget['bechdel_test'] == 'PASS']
bechdel_pass_writer = bechdel_pass_budget[bechdel_pass_budget['year']>=1990]
writer_pass = bechdel_pass_writer.groupby(['writer'])['bechdel_test'].count().nlargest(20)
writer_pass.plot(kind='bar', title='Writers with Highest # Bechdel Pass, 1990 Forward', ylabel='# of Passing Films',
         xlabel='director', figsize=(15, 8), width=0.9)
plt.xticks(rotation=45)


# In[17]:


bechdel_fail_budget = bechdel_imdb_budget[bechdel_imdb_budget['bechdel_test'] == 'FAIL']
bechdel_fail_writer = bechdel_fail_budget[bechdel_fail_budget['year']>=1990]
writer_fail = bechdel_fail_writer.groupby(['writer'])['bechdel_test'].count().nlargest(20)
writer_fail.plot(kind='bar', title='Writers with Highest # Bechdel Fail, 1990 Forward', ylabel='# of Passing Films',
         xlabel='director', figsize=(15, 8), width=0.9)
plt.xticks(rotation=45)


# Not a lot of crossover between writers who have many scripts that pass vs. fail. We're going to stay away from Woody Allen for obvious reasons, but the others in the top 20 are all prime candidates when shopping scripts. 

# <b>Insights Based on Bechdel Pass/Fail Rates Overall:</b>
# <ul>
#     <li>The proportion of movies passing the test has improved dramatically over time but is nowhere near 100%</li>
#     <li>The majority of films failing the Bechdel Test do have at least two named characters who talk to each other</li>
#     <li>The majority of films failing the Bechdel test have female characters that talk only about men, and are primarily accessories to the central male character(s).</li>
# </ul>
# 
# <b>Genres:</b>
# <ul>
#     <li>Comedy and Drama are the primary genres with the highest proportion of passing films</li>
#     <li>Action has the highest proportion of failing films</li>
#     <li>Drama, Romance, and Thriller films also have high pass rates for secondary/tertiary genre listing</li>
# </ul>
# 
# <b>Directors:</b>
# <ul>
#     <li>There is little crossover between the list of directors with the highest number of movies that pass and the list of directors with the highest number of movies that fail.</li>
#     <li>Removing the 5 who are in both lists gives us a shortlist of 14 directors that we will compare with profit margins and box office returns</li>
#     <li>Removing Woody Allen due to his problematic history with women gives us a shortlist of 13</li>
# </ul>
# 
# <b>Shortlist of Directors with Highest Number of Films Passing the Bechdel Test</b>
# <ul class="dashed">
#     <li>Tim Burton</li>
#     <li>Chris Columbus</li>
#     <li>Wes Craven</li>
#     <li>Adam Shankman</li>
#     <li>Catherine Hardwicke</li>
#     <li>John Madden</li>
#     <li>The Wachowski Sisters</li>
#     <li>Michael Bay</li>
#     <li>Paul Feig</li>
#     <li>Paul Anderson</li>
#     <li>Roland Emmerich</li>
#     <li>Zack Snyder</li>
#     <li>David Cronenberg</li>
#     <li>Denis Villeneuve</li>
# </ul>
# <p>It is worth noting that there are only two directors on this list who identify as female, further evidence of the dearth of women directors in Hollywood.</p>
# 
# <b>Writers:</b>
# <ul>
#     <li>There is even less crossover between the list of writers with the highest number of movies that pass vs. those with the highest number of movies that fail</li>
#     <li>Removing crossovers gives us a shortlist of 17 writers</li>
#     <li>There are many more women on the writer shortlist, which is encouraging</li>
# </ul>
# 
# <b>Shortlist of Writers with Highest Number of Films Passing the Bechdel Test</b>
# <ul class="dashed">
#     <li>The Wachowski Sisters</li>
#     <li>Paul W.S. Anderson</li>
#     <li>Jonathan Aibel, Glenn Berger</li>
#     <li>Rhett Reese, Paul Wernick</li>
#   <li>Richard Curtis</li>
#   <li>Christopher Markus, Stephen McFeely</li>
#   <li>Diablo Cody</li>
#  <li>Josh Appelbaum, André Nemec</li>
#  <li>Luc Besson</li>
#   <li>Melissa Rosenberg, Stephenie Meyer</li>
#   <li>Mike Leigh</li>
#  <li>Nicole Holofcener</li>
#    <li>Abby Kohn, Marc Silverstein</li>
#   <li>Andrew Jay Cohen, Brendan O'Brien</li>
#  <li>Cameron Crowe</li>
#  <li>Christina Hodson</li>
#   <li>Christopher Guest, Eugene Levy</li>
#   
# <b>Last but not least, Production Companies:</b>
#     <ul>
#         <li>I filtered for films made in the year 2000 and after so we can get an idea of films being made by contemporary companies</li>
#         <li>The goal is to find companies that are of similar size and budget to Savage productions and likely to make films that pass the Bechdel Test so we can investigate their successes and failures in greater detail. This competetive research will be a later phase of the project</li>
#         <li>Of those that had the highest number of films passing, only three were not also on the list of highest number of films failing:</li>
#         <ul>
#             <li>Dimension Films</li>
#             <li>Miramax</li>
#             <li>Blumhouse Productions</li>
#         </ul>
#         <li>We will focus our phase 2 competitive research on these three production companies   
#         

# In[ ]:





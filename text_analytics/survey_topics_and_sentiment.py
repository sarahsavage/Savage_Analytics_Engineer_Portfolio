##This script was developed for use in analyzing survey data with free-text fields, primarily the "anything else to share?" question
##The intent is that it can be used with any data set containing one or more free-text fields with minimal editing
##Bert was chosen as the best model to use for this purpose, but there are other options
##for this project, I decided against training and storing a bespoke model; investigation showed Bert to be as accurate

## 1. import relevant libraries

import pandas as pd
import os
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from transformers import pipeline


## 2. Create a dataframe from table

df_main = pd.read_csv('fact_outcome_surveys.csv')
##This is assuming the relevant data is stored in a table form in a queryable warehouse/database or already in csv format
##A connector can be set up using a tool like Airflow or Dataiku to automate as new surveys come in
##currently this process is done manually in a Jupyter notebook, after the table is downloaded from snowflake

## 3. Create filtered dataframe with just the join key and first text column
##remove Nan fields to exclude from topic creation
df_exp = df_main[['ENROLLMENT_ID', 'OVERALL_EXPERIENCE_TEXT']].dropna()

#cast text column as string to ensure that there aren't a few random floats or emojis thrown into the mix
df_exp['OVERALL_EXPERIENCE_TEXT'] = df_exp['OVERALL_EXPERIENCE_TEXT'].astype(str)

##check filtered dataframe
df_exp



# 4. Convert to list for vectorization
docs_exp = df_exp['OVERALL_EXPERIENCE_TEXT'].to_list()

os.environ["TOKENIZERS_PARALLELISM"] = "false"


# 5. Topics and Sentiment
# Initialize BERTopic Model
vectorizer_model = CountVectorizer(stop_words="english")
topic_model = BERTopic(
    vectorizer_model=vectorizer_model,
    calculate_probabilities=True,
    min_topic_size=50,
    verbose=True,
    n_gram_range=(1, 2),
    top_n_words=3
)

# Initialize Sentiment Analysis Model
sentiment_classifier = pipeline(
    'sentiment-analysis',
    model='cardiffnlp/twitter-roberta-base-sentiment-latest',
    truncation=True,
    max_length=512
)

# Perform topic classification and sentiment analysis in one pass
topics, probabilities = topic_model.fit_transform(docs_exp)
sentiment_results = sentiment_classifier(docs_exp)

# Collect data for the final DataFrame
topic_numbers = topics  # Topic classification results
sentiment_labels = [res['label'] for res in sentiment_results]
sentiment_scores = [res['score'] for res in sentiment_results]

# Create DataFrame for topic information
df_topics = pd.DataFrame({'Topic': list(topic_model.get_topics().keys()),
                          'topic_words': list(topic_model.get_topics().values())})
df_topic_info = pd.DataFrame(topic_model.get_topic_info()).iloc[1:].reset_index(drop=True)
df_topic_info['topic_words'] = df_topics['topic_words']

# Add topic and sentiment results to the original DataFrame
df_exp['Topic'] = topic_numbers
df_exp['sentiment_experience'] = sentiment_labels
df_exp['sentiment_score_experience'] = sentiment_scores

# Merge with topic information
df_exp_topic = df_exp.merge(df_topic_info, how='left', on='Topic')

# Drop coordinates if they exist
columns_to_drop = ['x_coordinate', 'y_coordinate']
df_exp_topic = df_exp_topic.drop(columns=[col for col in columns_to_drop if col in df_exp_topic.columns], axis=1)

# Filter out outlier topics (-1)
df_exp_topic = df_exp_topic[df_exp_topic['Topic'] != -1]

# Optional: Filter by topic size
min_topic_size = 50
large_topics = df_topic_info[df_topic_info['Count'] >= min_topic_size]['Topic']
df_exp = df_exp_topic[df_exp_topic['Topic'].isin(large_topics)]

# Rename columns for clarity
df_exp.rename(columns={
    'Topic': 'topic_number_experience',
    'Name': 'topic_name_experience',
    'Representation': 'representation_experience',
    'Representative_Docs': 'docs_experience',
    'topic_words': 'words_experience',
    'Count': 'count_experience_topic'
}, inplace=True)


# Final DataFrame
df_exp



# Repeat steps 3-5 for other text columns
# sentiment analysis for overall experience only, decision to be re-evaluated as needed

##Create filtered dataframe with just the join key and second text column
##remove Nan fields to exclude from topic creation
df_goal = df_main[['ENROLLMENT_ID', 'GOAL_OTHER']].dropna()

#cast text column as string to ensure that there aren't a few random floats or emojis thrown into the mix
df_goal['GOAL_OTHER'] = df_goal['GOAL_OTHER'].astype(str)

##check filtered dataframe
df_goal

# Convert to list for vectorization
docs_goal = df_goal['GOAL_OTHER'].to_list()

# Topic Classification with BERT 2nd column

# Define BERTopic Model
vectorizer_model = CountVectorizer(stop_words="english")
topic_model = BERTopic(
    vectorizer_model=vectorizer_model,
    calculate_probabilities=True,
    min_topic_size=20,
    verbose=True,
    n_gram_range=(1, 2),
    top_n_words=3
)

# Fit the topic model on the second text column
topics, probabilities = topic_model.fit_transform(docs_goal)
print(topic_model.get_topic_info())

# Create DataFrame for topic information
df_topics = pd.DataFrame({'Topic': list(topic_model.get_topics().keys()),
                           'topic_words': list(topic_model.get_topics().values())})
df_topic_info = pd.DataFrame(topic_model.get_topic_info()).iloc[0:].reset_index(drop=True)
df_topic_info['topic_words'] = df_topics['topic_words']

# Add coordinates only if topic count matches
fig_dict = topic_model.visualize_topics().to_dict()
if len(fig_dict['data']) == len(df_topic_info):
    df_topic_info['x_coordinate'] = [d['x'] for d in fig_dict['data']]
    df_topic_info['y_coordinate'] = [d['y'] for d in fig_dict['data']]
else:
    print("Mismatch in topic count. Skipping coordinate assignment.")


# Add topic information to the main DataFrame for column 2
df_goal['Topic'] = pd.Series(data=topics, index=df_goal.index)  # Ensure topics match the original DataFrame
df_topic = df_goal.merge(df_topic_info, how='left', on='Topic')  # Merge only with valid topics

# Drop coordinates if they exist
columns_to_drop = ['x_coordinate', 'y_coordinate']
df_goal = df_topic.drop(columns=[col for col in columns_to_drop if col in df_topic.columns], axis=1)

# Filter out outlier topics (-1)
df_goal = df_goal[df_goal['Topic'] != -1]  # Drop outliers

# Optional: Filter by topic size
min_topic_size = 20
large_topics = df_topic_info[df_topic_info['Count'] >= min_topic_size]['Topic']
df_goal = df_goal[df_goal['Topic'].isin(large_topics)]

# Rename columns for clarity
df_goal.rename(columns={
    'Topic': 'topic_number_goal',
    'Name': 'topic_name_goal',
    'Representation': 'representation_goal',
    'Representative_Docs': 'docs_goal',
    'topic_words': 'words_goal',
    'Count':'topic_count_goal'
}, inplace=True)

# Final DataFrame for column 2
df_goal



##Create filtered dataframe with just the join key and third text column
##remove Nan fields to exclude from topic creation
df_reason = df_main[['ENROLLMENT_ID', 'REASON_OTHER']].dropna()

#cast text column as string to ensure that there aren't a few random floats or emojis thrown into the mix
df_reason['REASON_OTHER'] = df_reason['REASON_OTHER'].astype(str)

##check filtered dataframe
df_reason


# Convert to list for vectorization
docs_reason = df_reason['REASON_OTHER'].to_list()

# Topic Classification with BERT 3rd column

# Define BERTopic Model
vectorizer_model = CountVectorizer(stop_words="english")
topic_model = BERTopic(
    vectorizer_model=vectorizer_model,
    calculate_probabilities=True,
    min_topic_size=50,
    verbose=True,
    n_gram_range=(1, 2),
    top_n_words=3
)

# Fit the topic model on the second text column
topics, probabilities = topic_model.fit_transform(docs_reason)
print(topic_model.get_topic_info())

# Create DataFrame for topic information
df_topics = pd.DataFrame({'Topic': list(topic_model.get_topics().keys()),
                           'topic_words': list(topic_model.get_topics().values())})
df_topic_info = pd.DataFrame(topic_model.get_topic_info()).iloc[0:].reset_index(drop=True)
df_topic_info['topic_words'] = df_topics['topic_words']

# Add coordinates only if topic count matches
fig_dict = topic_model.visualize_topics().to_dict()
if len(fig_dict['data']) == len(df_topic_info):
    df_topic_info['x_coordinate'] = [d['x'] for d in fig_dict['data']]
    df_topic_info['y_coordinate'] = [d['y'] for d in fig_dict['data']]
else:
    print("Mismatch in topic count. Skipping coordinate assignment.")


# Add topic information to the main DataFrame for column 3
df_reason['Topic'] = pd.Series(data=topics, index=df_reason.index)  # Ensure topics match the original DataFrame
df_topic = df_reason.merge(df_topic_info, how='left', on='Topic')  # Merge only with valid topics

# Drop coordinates if they exist
columns_to_drop = ['x_coordinate', 'y_coordinate']
df_reason = df_topic.drop(columns=[col for col in columns_to_drop if col in df_topic.columns], axis=1)

# Filter out outlier topics (-1)
df_reason = df_reason[df_reason['Topic'] != -1]  # Drop outliers

# Optional: Filter by topic size
min_topic_size = 50
large_topics = df_topic_info[df_topic_info['Count'] >= min_topic_size]['Topic']
df_reason = df_reason[df_reason['Topic'].isin(large_topics)]

# Rename columns for clarity
df_reason.rename(columns={
    'Topic': 'topic_number_reason',
    'Name': 'topic_name_reason',
    'Representation': 'representation_reason',
    'Representative_Docs': 'docs_reason',
    'topic_words': 'words_reason',
    'Count': 'topic_count_reason'
}, inplace=True)

# Final DataFrame for column 3
df_reason


#Last step, merge all these data frames into one
#merge on all common columns. Left join from original dataframe to preserve all responses
df_final= pd.merge(
	pd.merge(
		pd.merge(
			df_main,
			df_exp, on=['ENROLLMENT_ID','OVERALL_EXPERIENCE_TEXT'],
			how='left'
	    ),
		df_goal,on=['ENROLLMENT_ID','GOAL_OTHER'],
		how='left'
	),
    df_reason,on=['ENROLLMENT_ID','REASON_OTHER'],
	how='left'
)

#check final dataframe for desired fields
df_final


##Convert final dataframe to csv for reporting
df_final.to_csv('ocm_outcome_survey_text_analytics.csv', index=False)


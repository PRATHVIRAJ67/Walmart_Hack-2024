import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import string

# Load data
articles = pd.read_csv('articles.csv')
articles = articles[:10000]

# Define columns
cols = ['prod_name', 'product_type_name', 'product_group_name',
        'graphical_appearance_name', 'colour_group_name',
        'perceived_colour_value_name', 'perceived_colour_master_name',
        'department_name', 'index_name', 'index_group_name', 'section_name',
        'garment_group_name', 'detail_desc']

# Check for available columns
available_cols = [col for col in cols if col in articles.columns]

if available_cols:
    articles['combined_cols'] = articles[available_cols].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
else:
    raise KeyError("None of the specified columns are available in the DataFrame")

articles = articles[['article_id', 'combined_cols']]

# Text processing function
def text_process(desc):
    articles['combined_cols'].fillna(value='', inplace=True)  # Fill the null values with empty string
    # Remove punctuation
    noPunc = [c for c in desc if c not in string.punctuation]
    noPunc = ''.join(noPunc)
    noPunc = noPunc.split()
    # Remove stopwords
    stopword = stopwords.words('english')
    desc_stopwords = [word.lower() for word in noPunc if word.lower() not in stopword]
    # Replace words with their respective stems
    stemmer = PorterStemmer()
    desc_cleaned = [stemmer.stem(word) for word in desc_stopwords]
    return desc_cleaned

# TF-IDF Vectorizer
tfidf = TfidfVectorizer(analyzer=text_process)
tfidf_matrix = tfidf.fit_transform(articles['combined_cols'])

# Cosine Similarity
cos_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
indices = pd.Series(articles.index, index=articles['article_id']).drop_duplicates()

# Recommendation function
def recommendations(article_id):
    i = indices[article_id]  # Index of the articles that match the given article
    sim_scores = list(enumerate(cos_sim[i]))  # Similarity scores of all articles w.r.t. to the given article
    sim_scores.sort(key=lambda x: x[1], reverse=True)  # Sort the similarity scores in descending order
    # Get the scores of the 10 most similar articles
    sim_scores = sim_scores[:10]
    # Get the article indices
    article_indices = [score[0] for score in sim_scores]
    return articles['article_id'].iloc[article_indices].values

# Predict recommendations
predict_recom = recommendations(118458003)
print(predict_recom)

# Save the similarity matrix to a file using pickle
with open('recommender.pkl', 'wb') as file:
    pickle.dump(cos_sim, file)

# Search result function
def search_result(desc):
    search_tfidf = tfidf.transform([desc])
    cos_sim = cosine_similarity(search_tfidf, tfidf_matrix)
    sim_scores = list(enumerate(cos_sim[0]))
    sim_scores.sort(key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[:50]
    article_indices = [score[0] for score in sim_scores]
    return articles['article_id'].iloc[article_indices].values

# Test search result
search_result("jogger women")

# Save TF-IDF vectorizer and matrix to file
with open('tfidf.pkl', 'wb') as file:
    pickle.dump(tfidf, file)

with open('tfidf_matrix.pkl', 'wb') as file:
    pickle.dump(tfidf_matrix, file)

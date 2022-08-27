import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import treetaggerwrapper as tt

def preprocess(df):
    df = df.apply(lambda x: x.lower())
    df = df.reset_index(drop=True)
    df = df.str.translate(str.maketrans('', '', string.punctuation.replace('.','')))
    df = df.str.replace('\d+', '')
    
    #lemmatization
    path = 'TreeTagger/tree-tagger-MacOSX-3.2.3'
    t_tagger = tt.TreeTagger(TAGLANG ='en', TAGDIR =path)

    df = df.apply(lambda x: t_tagger.tag_text(x))
    df = df.apply(lambda x: [t.split('\t')[-1] for t in x])
    df = df.apply(lambda x: ' '.join(x))
    return df

TOP_K_KEYWORDS = 10 # top k number of keywords to retrieve in a ranked document

def sort_coo(coo_matrix):
    """Sort a dict with highest score"""
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)

def extract_topn_from_vector(feature_names, sorted_items, topn=10):
    """get the feature names and tf-idf score of top n items"""
    
    #use only topn items from vector
    sorted_items = sorted_items[:topn]

    score_vals = []
    feature_vals = []
    
    # word index and corresponding tf-idf score
    for idx, score in sorted_items:
        
        #keep track of feature name and its corresponding score
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])

    #create a tuples of feature, score
    results= {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]]=score_vals[idx]
    
    return results

def get_keywords(vectorizer, feature_names, doc):
    """Return top k keywords from a doc using TF-IDF method"""

    #generate tf-idf for the given document
    tf_idf_vector = vectorizer.transform([doc])
    
    #sort the tf-idf vectors by descending order of scores
    sorted_items=sort_coo(tf_idf_vector.tocoo())

    #extract only TOP_K_KEYWORDS
    keywords=extract_topn_from_vector(feature_names,sorted_items,TOP_K_KEYWORDS)
    
    return list(keywords.keys())

def get_top_keywords(df, STOPWORDS=list(), top_n = 30):
    df = preprocess(df)
    STOPWORDS += list(stopwords.words('english'))
    corpora = df.to_list() 
    vectorizer = TfidfVectorizer(stop_words=STOPWORDS, smooth_idf=True, use_idf=True)
    vectorizer.fit(corpora)
    feature_names = vectorizer.get_feature_names_out()
    
    # Get top_keywords from TFIDF for each document(review)
    corpora_top_keywords = []
    for doc in corpora:
        d = {}
        d['full_text'] = doc
        d['top_keywords'] = get_keywords(vectorizer, feature_names, doc)
        corpora_top_keywords.append(d)
    corpora_top_keywords = pd.DataFrame(corpora_top_keywords)

    from collections import defaultdict
    word_frequency = defaultdict(int)
    
    # Count weight for each word based on its position in top_keywords
    for i_row in range(corpora_top_keywords.shape[0]):
        words = corpora_top_keywords.iloc[i_row].top_keywords
        for i, word in enumerate(words):
            word_frequency[word] += 1 / (1 + i)     

    word_frequency = dict(sorted(word_frequency.items(), key=lambda item: item[1], reverse=True)[:top_n])
    return word_frequency
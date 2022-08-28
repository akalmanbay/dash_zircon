from typing import Dict, List, Tuple
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords as nltk_stopwords
import treetaggerwrapper as tt
import string
from collections import defaultdict


def sort_coo(coo_matrix):
    """Sort a dict with highest score"""
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)


class Extractor:
    def __init__(
        self, top_k_keywords: int = 10, top_n: int = 30, stopwords: List[str] = None
    ):
        self.top_k_keywords = top_k_keywords
        self.top_n = top_n
        self.stopwords = list(nltk_stopwords.words("english"))
        if stopwords is not None:
            self.stopwords += stopwords

        path = "TreeTagger/tree-tagger-MacOSX-3.2.3"
        self.t_tagger = tt.TreeTagger(TAGLANG="en", TAGDIR=path)
        # self.a = number

    def _preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.apply(lambda x: str(x).lower())
        df = df.reset_index(drop=True)
        df = df.str.translate(
            str.maketrans("", "", string.punctuation.replace(".", ""))
        )
        df = df.str.replace("\d+", "")

        # lemmatization
        df = df.apply(lambda x: self.t_tagger.tag_text(x))
        df = df.apply(lambda x: [t.split("\t")[-1] for t in x])
        df = df.apply(lambda x: " ".join(x))
        return df.to_list()

    def _extract_topn_from_vector(
        self, feature_names: List[str], sorted_items: Tuple[int, float]
    ) -> Dict[str, float]:
        """get the feature names and tf-idf score of top n items"""

        # use only topn items from vector
        sorted_items = sorted_items[: self.top_k_keywords]

        score_vals = []
        feature_vals = []

        # word index and corresponding tf-idf score
        for idx, score in sorted_items:
            # keep track of feature name and its corresponding score
            score_vals.append(round(score, 3))
            feature_vals.append(feature_names[idx])

        # create a tuples of feature, score
        results = {}
        for idx in range(len(feature_vals)):
            results[feature_vals[idx]] = score_vals[idx]

        return results

    def _get_keywords(self, vectorizer, feature_names, doc):
        """Return top k keywords from a doc using TF-IDF method"""
        # generate tf-idf for the given document
        tf_idf_vector = vectorizer.transform([doc])

        # sort the tf-idf vectors by descending order of scores
        sorted_items = sort_coo(tf_idf_vector.tocoo())

        # extract only TOP_K_KEYWORDS
        keywords = self._extract_topn_from_vector(feature_names, sorted_items)
        return list(keywords.keys())

    def get_top_keywords(self, df: pd.DataFrame, STOPWORDS=list()):
        corpora = self._preprocess(df)
        vectorizer = TfidfVectorizer(
            stop_words=self.stopwords, smooth_idf=True, use_idf=True
        )
        vectorizer.fit(corpora)
        feature_names = vectorizer.get_feature_names_out()

        # Get top_keywords from TFIDF for each document(review)
        corpora_top_keywords = []
        for doc in corpora:
            d = {}
            d["full_text"] = doc
            d["top_keywords"] = self._get_keywords(vectorizer, feature_names, doc)
            corpora_top_keywords.append(d)
        corpora_top_keywords = pd.DataFrame(corpora_top_keywords)

        word_frequency = defaultdict(int)

        # Count weight for each word based on its position in top_keywords
        for i_row in range(corpora_top_keywords.shape[0]):
            words = corpora_top_keywords.iloc[i_row].top_keywords
            for i, word in enumerate(words):
                word_frequency[word] += 1 / (1 + i)

        word_frequency = dict(
            sorted(word_frequency.items(), key=lambda item: item[1], reverse=True)[
                : self.top_n
            ]
        )
        return word_frequency

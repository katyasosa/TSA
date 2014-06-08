from __future__ import unicode_literals

import joblib
import marisa_trie
from sklearn.feature_extraction.text import CountVectorizer

from . import _speedups

# See https://gist.github.com/kmike/7814472
# hack to store vocabulary in MARISA Trie
class _MarisaVocabularyMixin(object):

    def fit_transform(self, raw_documents, y=None):
        super(_MarisaVocabularyMixin, self).fit_transform(raw_documents)
        self._freeze_vocabulary()
        return super(_MarisaVocabularyMixin, self).fit_transform(raw_documents, y)

    def _freeze_vocabulary(self):
        if not self.fixed_vocabulary:
            self.vocabulary_ = marisa_trie.Trie(self.vocabulary_.keys())
            self.fixed_vocabulary = True
            del self.stop_words_


class NgramVectorizer(_MarisaVocabularyMixin, CountVectorizer):
    def __init__(self, article_categories_path, **kwargs):
        kwargs.update({
            "decode_error": "ignore",
            "analyzer": "char",
        })

        # A 'marisa_trie.ByteTrie' which maps articles to Wikipedia
        # categories.
        self.article_categories = joblib.load(article_categories_path)
        super(NgramVectorizer, self).__init__(**kwargs)

    def fit_transform(self, docs, y=None):
        self.known_words = marisa_trie.Trie(
                word for doc in docs for word in self._collect_words(doc))
        return super(NgramVectorizer, self).fit_transform(docs, y)

    def _char_ngrams(self, doc):
        """Tokenize a document into a sequence of character bi-ngrams.

        >>> v = NgramVectorizer(ngram_range=(3, 3))
        >>> v._char_ngrams(u"mama mila ramu")
        [u'***mam', u'mama m', u'a mila', u'ila ra', u' ramu', u'mu****']
        """
        if self.fixed_vocabulary:
            doc = self._replace_missing_words(doc)

        n, n = self.ngram_range
        return _speedups._char_bi_ngrams(doc, n, "*")

    def _collect_words(self, doc):
        preprocess = self.build_preprocessor()
        tokenize = self.build_tokenizer()
        return tokenize(preprocess(self.decode(doc)))

    def _replace_missing_words(self, doc):
        acc, article_categories = [], self.article_categories
        for word in self._collect_words(doc):
            if word not in self.known_words:
                for replacement in article_categories.iterkeys(word.lower()):
                    word = replacement
                    break

            acc.append(word)

        return " ".join(acc)

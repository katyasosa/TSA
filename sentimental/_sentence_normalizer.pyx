from __future__ import unicode_literals, print_function

import HTMLParser
import re
import string

import marisa_trie
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords


POSITIVE_SMILEYS = [
    ':-)', ':)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}',
    ':^)', ':っ)', ':-D', ':D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD',
    '=-D', '=D', '=-3', '=3', 'B^D', ':-))', ':\'-)', ':\')', ':*', ':^*',
    '(', '\'}{\'', ')', ';-)', ';)', '*-)', '*)', ';-]', ';]', ';D',
    ';^)', ':-,', '>:P', ':-P', ':P', 'X-P', 'x-p', 'xp', 'XP', ':-p',
    ':p', '=p', ':-Þ', ':Þ', ':þ', ':-þ', ':-b', ':b', 'd:', 'O:-)',
    '0:-3', '0:3', '0:-)', '0:)', '0;^)', '\o/', '<3'
]

NEGATIVE_SMILEYS = [
    '>:[', ':-(', ':(', ':-c', ':c', ':-<', ':っC', ':<', ':-[', ':[',
    ':{', ';(', ':-||', ':@', '>:(', ':\'-(', ':\'(', 'D:<', 'D:', 'D8',
    'D;', 'D=', 'DX', 'v.v', 'D-\':', '>:\\', '>:/', ':-/', ':-.', ':/',
    ':\\', '=/', '=\\', ':L', '=L', ':S', '>.<', ':|', ':-|', ':$', 'ಠ_ಠ',
    '</3'
]

re_positive_smiley = re.compile("|".join(map(re.escape, POSITIVE_SMILEYS)))
re_negative_smiley = re.compile("|".join(map(re.escape, NEGATIVE_SMILEYS)))

re_username = re.compile("@\w+")
re_digits = re.compile("\d+")
re_url = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|"
                    "[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")


def normalize_repeats(unicode chunk):
    """Normalizes repetitive characters in a given string.

    >>> normalize_repeats("helllooooo!!!!")
    'helloo!!'
    """
    acc = []
    cdef int count = 0
    cdef int i
    for i in range(1, len(chunk)):
        if chunk[i] == chunk[i - 1]:
            count += 1
        else:
            acc.append(chunk[i - 1] * min(count + 1, 2))
            count = 0

    acc.append(chunk[-1] * min(count + 1, 2))
    return "".join(acc)



class SentenceNormalizer(object):
    stemmer = SnowballStemmer("english")
    stopwords = marisa_trie.Trie(stopwords.words("english"))
    html_parser = HTMLParser.HTMLParser()

    def __init__(self, path):
        self.abbr = marisa_trie.BytesTrie()
        self.abbr.load(path)

    def __call__(self, unicode  text):
        text = self.html_parser.unescape(text)
        text = re_username.sub("USER", text)
        text = re_url.sub("URL", text)
        text = re_digits.sub("42", text)
        text = re_positive_smiley.sub("+", text)
        text = re_negative_smiley.sub("-", text)
        text = normalize_repeats(text)
        # TODO: smileys

        chunks = []
        for s in sent_tokenize(text):
            for chunk in word_tokenize(s):
                if chunk in self.stopwords:
                    continue
                elif chunk in self.abbr:
                    expansions = self.abbr[chunk]
                    for expanded_chunk in word_tokenize(expansions[0]):
                        chunks.append(self.stemmer.stem(expanded_chunk))
                else:
                    chunks.append(chunk)

        return " ".join(chunks)

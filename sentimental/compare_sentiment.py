# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import time

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import classification_report
from sklearn.naive_bayes import BernoulliNB, MultinomialNB

from .bayesian_naive_bayes import BernoulliBNB
from .ngrams import NgramVectorizer


def read_dataset(path, baseline=False):
    if baseline:
        df = pd.read_csv(path, encoding="ISO-8859-1",
                         usecols=["polarity", "text"],
                         names=["polarity", "status_id", "date", "query",
                                "user", "text"])
        df["polarity"] = df["polarity"] // 2 - 1
        mask = df["polarity"] != 0  # Drop neutral samples.
        df = df.ix[mask]
    else:
        df = pd.read_csv(path, names=["polarity", "text"])
    return df["text"].values, df["polarity"].values


def compare_classifiers(X_train, y_train, X_test, y_test, pipeline):
    classifiers = [
        BernoulliNB(),
        MultinomialNB(),
        BernoulliBNB()
    ]

    X_train = pipeline.fit_transform(X_train, y_train)
    X_test = pipeline.transform(X_test)

    for clf in classifiers:
        print("Fitting {0!r} ...".format(clf.__class__.__name__), end=" ")
        start = time.time()
        clf.fit(X_train, y_train)
        print("done in {0}s".format(int(time.time() - start)))
        print(classification_report(y_test, clf.predict(X_test)))


def fit_baseline(X_train, y_train, X_test, y_test):
    pipeline = NgramVectorizer("./article_categories_en.nt.dump",
                               ngram_range=(3, 3))
    X_train = pipeline.fit_transform(X_train, y_train)
    X_test = pipeline.transform(X_test)

    X_train = pipeline.fit_transform(X_train, y_train)
    X_test = pipeline.transform(X_test)

    classifiers = [
        BernoulliNB(),
        MultinomialNB(),
        BernoulliBNB()
    ]
    for clf in classifiers:
        print("Fitting {0!r} ...".format(clf.__class__.__name__), end=" ")
        start = time.time()
        clf.fit(X_train, y_train)
        print("done in {0}s".format(int(time.time() - start)))
        print(classification_report(y_test, clf.predict(X_test)))



if __name__ == "__main__":
    X_test, y_test = read_dataset("./stashdump.normalized.csv")

    print(">>> Baseline")
    X_train, y_train = read_dataset(
        "./training.1600000.processed.noemoticon.csv", baseline=True)
    pipeline = CountVectorizer("./article_categories_en.nt.dump",
                               analyzer="word")
    compare_classifiers(X_train, y_train, X_test, y_test, pipeline)

    print(">>> The new shit!")
    X_train, y_train = read_dataset("./training.1600000.normalized.csv")
    pipeline = NgramVectorizer("./article_categories_en.nt.dump",
                               ngram_range=(3, 3))
    compare_classifiers(X_train, y_train, X_test, y_test, pipeline)

from __future__ import print_function

__all__ = ["get_article_categories"]

import csv
import os
import tempfile

import joblib
import marisa_trie
from networkx import DiGraph

MEMORY = joblib.Memory(cachedir=tempfile.mkdtemp(), verbose=0)

TYPE, CONCEPT, LABEL, BROADER, SUBJECT = [
    "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>",
    "<http://www.w3.org/2004/02/skos/core#Concept>",
    "<http://www.w3.org/2004/02/skos/core#prefLabel>",
    "<http://www.w3.org/2004/02/skos/core#broader>",
    "<http://purl.org/dc/terms/subject>"
]


def get_article_categories(skos_categories_path, article_categories_path):
    def successors(category):
        return len(g.successors(category_labels[category]))

    def iter_articles():
        f = open(article_categories_path)
        current, acc = None, []
        for chunks in csv.reader(f, delimiter=" "):
            if chunks[1] != SUBJECT:
                continue

            source, target = chunks[0], chunks[2]
            if source != current:
                if acc:
                    # We want to assign to each article the most specific
                    # label possible. The current heuristic is to pick th
                    # value with the minimum successors in the graph.
                    most_specific = min(acc, key=successors)
                    yield ((current[current.rfind("/") + 1:-1]
                            .lower().decode("utf-8")),
                           most_specific.encode("utf-8"))
                    del acc[:]

                current = source
            else:
                category = target[target.rfind(":") + 1:-1] .decode("utf-8")
                # Surprisingly, some categories are missing in the SKOS file,
                # so we just skip them.
                if category in category_labels:
                    acc.append(category)

        f.close()

    ac_dump_path = article_categories_path + ".dump"
    if os.path.exists(ac_dump_path):
        return joblib.load(ac_dump_path)

    print("Computing article categories...", end=" ")
    category_labels = _get_labels(skos_categories_path)
    g = _get_category_graph(skos_categories_path)
    article_categories = marisa_trie.BytesTrie(
        (article, categories) for article, categories in iter_articles())
    print("done")
    joblib.dump(article_categories, ac_dump_path, compress=3)


def _get_category_graph(skos_categories_path):
    print("Computing category graph...", end=" ")
    category_labels = _get_labels(skos_categories_path)
    g = DiGraph()
    with open(skos_categories_path) as f:
        for chunks in csv.reader(f, delimiter=" "):
            if chunks[1] == BROADER:
                source, target = chunks[0], chunks[2]
                source, target = (
                    source[source.rfind(":") + 1:-1].decode("utf-8"),
                    target[target.rfind(":") + 1:-1].decode("utf-8")
                )

                # The original relation is "broader", but for our purposes
                # "wider" is more appropriate.
                g.add_edge(category_labels[target], category_labels[source])
            elif chunks[1] == TYPE:
                source = chunks[0]
                source = source[source.rfind(":") + 1:-1].decode("utf-8")
                g.add_node(category_labels[source])
    print("done")
    return g


@MEMORY.cache
def _get_labels(skos_categories_path):
    def iter_categories():
        acc = set()
        f = open(skos_categories_path)
        for chunks in csv.reader(f, delimiter=" "):
            if chunks[1] == BROADER:
                target = chunks[2]
                acc.add(target[target.rfind(":") + 1:-1])
            elif chunks[1] == TYPE:
                source = chunks[0]
                acc.add(source[source.rfind(":") + 1:-1])

        f.close()
        return (s.decode("utf-8") for s in acc)

    print("Computing labels...", end=" ")
    category_labels = marisa_trie.Trie(iter_categories())
    print("done")
    return category_labels


if __name__ == "__main__":
    # Go download these from 'http://wiki.dbpedia.org/Downloads39'
    skos_categories_path = "./skos_categories_en.nt"
    article_categories_path = "./article_categories_en.nt"
    article_categories = get_article_categories(
        skos_categories_path, article_categories_path)

# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import csv
import sys

import numpy as np
import pandas as pd

from _sentence_normalizer import SentenceNormalizer


if __name__ == "__main__":
    try:
        [src_path, dst_path] = sys.argv[1:]
    except ValueError:
        print("usage: script.py path/to/src path/to/dst", file=sys.stderr)
        sys.exit(1)

    norm = SentenceNormalizer("abbr.marisa")
    df = pd.read_csv(src_path, error_bad_lines=False, encoding="ISO-8859-1",
                     quoting=csv.QUOTE_ALL,
                     usecols=["polarity", "text"],
                     names=["polarity", "status_id", "date", "query",
                            "user", "text"])

    df["polarity"] = (df["polarity"] / 2 - 1).astype(np.int8)
    mask = df["polarity"] != 0  # Drop neutral samples.
    df = df.ix[mask]

    df["text"] = df["text"].apply(norm)
    df.to_csv(dst_path, cols=["polarity", "text"], encoding="utf-8",
              header=False, index=False, quoting=csv.QUOTE_ALL)

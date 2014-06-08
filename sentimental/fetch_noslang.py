from __future__ import print_function

import string
import sys

import requests
from lxml import html
from marisa_trie import BytesTrie


def iter_noslang():
    fucking_shit = {
        "a**": "ass",
        "b*****d": "bastard",
        "b***h": "bitch",
        "c**k": "cock",
        "c**t": "cunt",
        "c**": "cum",
        "d**k": "dick",
        "d**n": "damn",
        "d***o": "dildo",
        "d****e": "douche",
        "f**": "fag",
        "f**k": "fuck",
        "f*ck": "fuck",
        "h**e": "hole",
        "n****r": "nigger",
        "n***a": "nigga",
        "p***y": "pussy",
        "s**t": "shit",
        "w***e": "whore",
    }

    for resource in ["dictionary", "rejects"]:
        for ch in "1" + string.lowercase:  # '1' for #
            url = "http://www.noslang.com/{}/{}".format(resource, ch)
            print("Processing " + url)
            r = requests.get(url)
            if not r.ok:
                print("Skipping {} (status code {})".format(ch, r.status_code),
                      file=sys.stderr)

            page = html.fromstring(r.text)
            for abbr in page.cssselect("abbr"):
                a = abbr.getprevious()
                definition = abbr.attrib["title"].lower()
                if definition in fucking_shit:
                    definition = fucking_shit[definition]
                else:
                    for stars, replacement in fucking_shit.iteritems():
                        definition = definition.replace(stars, replacement)

                yield a.attrib["name"].decode("utf-8"), definition


if __name__ == "__main__":
    try:
        [path] = sys.argv[1:]
    except ValueError:
        print("Usage: [prog] path/to/trie", file=sys.stderr)
        sys.exit(1)

    abbr = BytesTrie(iter_noslang())
    abbr.save(path)

from __future__ import print_function

import cPickle
import csv
import sys
import time
from collections import defaultdict

import tweepy


def collect_tweets(api, tag, count):
    print(">>> Fetching search results...", end=" ")
    q = list(take(iter_results(api, tag, lang="en",
                               result_type="recent"), count))
    print("done")
    tweets = {}
    while q:
        status = q.pop()
        if getattr(status, "retweeted_status", False):
            continue  # Omit retweets.

        in_reply_to_status_id = status.in_reply_to_status_id
        if (in_reply_to_status_id is not None and
            in_reply_to_status_id not in tweets):
            try:
                q.append(api.get_status(in_reply_to_status_id))
            except tweepy.TweepError as e:
                handle_error(e)

            q.extend(iter_replies(api, status.user.name, status.id))

        tweets[status.id] = status

    return tweets


def take(it, count):
    for i in xrange(count):
        yield next(it)


def handle_error(e):
    args, = e.message
    if args["code"] == 88:
        print(args["message"] + ", sleeping for 5M...", end=" ")
        time.sleep(300)
        print("woke up!")
    else:
        print(e)


def iter_results(api, *args, **kwargs):
    kwargs.setdefault("count", 100)

    max_id = float("inf")
    while True:
        try:
            for status in api.search(*args, **kwargs):
                max_id = min(max_id, status.id)
                yield status
        except tweepy.TweepError as e:
            handle_error(e)

        kwargs["max_id"] = max_id


def iter_replies(api, user, status_id):
    try:
        for status in api.search("@" + user, since_id=status_id, count=100):
            if status.in_reply_to_status_id == status_id:
                yield status
    except tweepy.TweepError as e:
        handle_error(e)


def build_tree(tweets):
   forest = defaultdict(list)
   for status_id in sorted(tweets):
      status = tweets[status_id]
      in_reply_to_status_id = status.in_reply_to_status_id
      if in_reply_to_status_id is not None:
         forest[in_reply_to_status_id].append(status_id)

      forest.setdefault(status_id, [])

   return forest


def main(tag, count):
    consumer_token = "qaxwA1MNvx2ilaBQaql4g"
    consumer_secret = "ok5l42lywxjEeh460xTy8EMUUQzMkVBhorITv82Yc"

    key = "115023328-B3LMKWYXNS86M5YiS7BT8CSAvTFR8E9thUYIzGmd"
    secret = "wgcM1iAZPvuSZBogjtEJ3B5VZRCb3vwCnBqqi9EGgA"

    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
    auth.set_access_token(key, secret)

    api = tweepy.API(auth)

    print(">>> Searching for {0!r} (max. {1} results)".format(tag, count))
    tweets = collect_tweets(api, tag, count)
    print(">>> Found {0} tweets".format(len(tweets)))

    with open("{0}-{1}.csv".format(tag, count), "w") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["status_id", "text"])
        for status_id, status in tweets.iteritems():
            writer.writerow([0, status_id, status.created_at, tag,
                             status.user.screen_name,
                             status.text.encode("utf-8")])

    with open("{0}-{1}.dump".format(tag, count), "wb") as f:
        cPickle.dump(tweets, f)


if __name__ == "__main__":
    try:
        tag, count = sys.argv[1:]
        count = int(count)
    except ValueError:
        sys.exit("Usage: [twitter] TAG COUNT")

    main(tag, count)

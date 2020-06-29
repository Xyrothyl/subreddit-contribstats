import praw
import datetime
from datetime import datetime as dt
import argparse

def evalStat(bot, feed, win, aux):
    """Calculate user statistics for a given subreddit.

    Keyword arguments:
    bot -- valid Reddit application, can be read-only
    feed -- feed to draw from
    win -- max. number of days ago a submission could have been posted
    aux -- statistical aggregation function taking an int and a post
    """
    stat = {}
    for post in feed(limit=None):
        time = dt.utcfromtimestamp(post.created_utc)
        if dt.now() - time > \
           datetime.timedelta(days=win):
            break;
        if post.link_flair_text == "MOD POST":
            continue
        if post.author in stat:
            stat[post.author] = aux(stat[post.author], post)
        else:
            stat[post.author] = aux(0, post)
    lst = list(stat.items())
    lst.sort(key=lambda x: x[1], reverse=True)
    return lst

def makeParser():
    """Generate user-facing arg-parser for subreddit-contribstats"""

    parser = argparse.ArgumentParser()
    parser.add_argument("-S", "--stat", type=str,
                        default="posts",
                        help="select statistic to analyze")
    parser.add_argument("-s", "--subreddit", type=str,
                        default="historicalworldpowers",
                        help="select subreddit to scan")
    parser.add_argument("-f", "--feed", type=str,
                        choices=["hot", "new"],
                        default="new",
                        help="select feed to read from")
    parser.add_argument("-w", "--window", type=float,
                        default=7,
                        help="maximum age of post, in days")
    parser.add_argument("-m", "--minimum", type=int,
                        help="minimum score required to display user")
    parser.add_argument("-r", "--results", type=int,
                        help="limit maximum number of returned results")
    parser.add_argument("-n", action="store_true",
                        help="number results")
    parser.add_argument("-G", "--get_post", type=int,
                        help="""instead of accumulating statistics, """
                             """print out the nth post in the feed.""")
    return parser

def printPost(sub, feed, n):
    """Print a single post from the given subreddit.

    Keyword arguments:
    sub -- the name of a subreddit
    feed -- the feed to draw from, e.g. 'hot', 'new', etc.
    n -- the number of the post to output
    """

    count = 0
    for post in getattr(sub, feed)(limit=None):
        time = dt.utcfromtimestamp(post.created_utc)
        if post.link_flair_text == "MOD POST":
            continue
        elif count < n:
            count += 1
        else:
            print("""Printing the {}th most {} post to r/{}...\n"""
                  """  Title:  {}\n"""
                  """  Author: {}""".format(
                      n, feed, sub, post.title, post.author.name))
            if post.selftext:
                print("-----\n{}\n-----".format(post.selftext))
            else:
                print("-----\n<{}>\n-----".format(post.url))
            return

def main():
    stats = {
        "posts": lambda base, post: base + 1,
        "chars": lambda base, post: base + len(post.selftext),
        "words": lambda base, post: base + len(post.selftext.split()),
        "karma": lambda base, post: base + post.score
    }

    args = makeParser().parse_args()

    try:
        bot = praw.Reddit('bot1')
        sub = bot.subreddit(args.subreddit)
        aux = stats[args.stat]
    except KeyError:
        print("invalid option supplied for --stat;")
        print("\tvalid options include:", list(stats.keys()))
        return

    if args.get_post is not None:
        printPost(sub, args.feed, args.get_post)
        return

    lst = evalStat(bot, getattr(sub, args.feed), args.window, aux)
    count = 0
    for author, num in lst:
        if args.results and count >= args.results:
            break
        if args.minimum and num < args.minimum:
            break;
        if args.n:
            print ("{:>3} {:22}: {:>5}".format(count+1, author.name, num))
        else:
            print ("{:22}: {:>5}".format(author.name, num))
        count += 1

if __name__ == "__main__":
    main()

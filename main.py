import praw
import datetime
from datetime import datetime as dt
from sys import argv
window = 14

def printStat(bot, sub, aux):
    stats = {}
    for post in sub.new(limit=None):
        time = dt.utcfromtimestamp(post.created_utc)
        if dt.now() - time > \
           datetime.timedelta(days=window):
            break;
        if post.link_flair_text == "MOD POST":
            continue
        if post.author in stats:
            stats[post.author] = aux(stats[post.author], post)
        else:
            stats[post.author] = aux(0, post)
    lst = list(stats.items())
    lst.sort(key=lambda x: x[1], reverse=True)
    for author, num in lst:
        print ("{:22}: {:>5}".format(author.name, num))

def main():
    def countPosts(base, post):
        return base + 1
    def countChars(base, post):
        return base + len(post.selftext)
    def countWords(base, post):
        return base + len(post.selftext.split)

    bot = praw.Reddit('bot1')
    hwp = bot.subreddit("historicalworldpowers")

    printStat(bot, hwp, countPosts)

if __name__ == "__main__":
    main()

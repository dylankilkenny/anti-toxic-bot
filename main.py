from prawcore.exceptions import PrawcoreException
import praw
from configparser import ConfigParser
import requests
import json

parser = ConfigParser()
parser.read('config.conf')


def getComments(user):
    try:
        url = 'https://api.pushshift.io/reddit/search/comment/?subreddit=btc&author=%s&size=1000' % user
        r = requests.get(url)
        data = json.loads(r.text)
        return data['data']
    except json.decoder.JSONDecodeError:
        log('Decoding JSON has failed')
        print(r.text)


def sumCommentScore(comments):
    totalscore = 0
    for c in comments:
        totalscore = totalscore + c['score']
    return totalscore


def stats(comments):
    totalscore = 0
    lowestscore = 0
    highestscore = 0
    for c in comments:
        if c['score'] < lowestscore:
            lowestscore = c['score']
        if c['score'] > highestscore:
            highestscore = c['score']
        totalscore = totalscore + c['score']

    print("Total Comments: %s" % len(comments))
    print("Total Score: %s" % totalscore)
    print("Highest Score: %s" % highestscore)
    print("Lowest Score: %s" % lowestscore)


def main():
    reddit = praw.Reddit(
        client_id=parser.get('reddit', 'client_id'),
        client_secret=parser.get('reddit', 'client_secret'),
        password=parser.get('reddit', 'password'),
        user_agent=parser.get('reddit', 'user_agent'),
        username=parser.get('reddit', 'username'))

    subreddit = reddit.subreddit('btc')
    post_count = 0
    for c in subreddit.stream.comments():
        if post_count > 100:
            redditor = c.author.name
            redditor_karma = sumCommentScore(getComments(redditor))
            comment = "The Redditor /u/%s has low karma in this subreddit" % redditor
            if redditor_karma < 0:
                print(comment)
                reply = c.reply(comment)
                print("Comment ID: %s" % c.id)
                stats(getComments(redditor))
        post_count += 1


if __name__ == "__main__":
    main()

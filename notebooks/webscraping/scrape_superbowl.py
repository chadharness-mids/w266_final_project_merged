import praw
import configparser
import csv

# Config Things
config = configparser.ConfigParser()
config.read('reddit.config')
reddit = praw.Reddit(client_id=config['REDDIT_CONFIG']['client_id'],
                     client_secret=config['REDDIT_CONFIG']['client_secret'],
                     password=config['REDDIT_CONFIG']['password'],
                     user_agent=config['REDDIT_CONFIG']['user_agent'],
                     username=config['REDDIT_CONFIG']['username'])

# Setup Submission
game_thread_url = 'https://www.reddit.com/r/nfl/comments/5sapal/super_bowl_51_game_thread_new_england_patriots/'
submission = reddit.submission(url=game_thread_url)
print("Number of Comments in Game Thread: {}".format(submission.num_comments))

# Pull Comments

submission.comments.replace_more(limit=0)
comment_queue = submission.comments[:]  # Seed with top-level

with open("output.csv", "wb") as output:
    writer = csv.writer(output)
    while comment_queue:
        comment = comment_queue.pop(0)
        print("=============NEW COMMMENT=============")
        print('Comment ID:', comment.id)
        print('Comment Body:', comment.body)
        print('Comment Author:', comment.author)
        print('Comment Author Flair CSS:', comment.author_flair_css_class)
        print('Comment Author Flair Text', comment.author_flair_text)
        print('Comment Body Controversaility:', comment.controversiality)
        print('Comment Created:', comment.created)
        print('Comment Created UTC:', comment.created_utc)
        print('Comment Depth', comment.depth)
        print('Comment Downvotes', comment.downs)
        print('Comment UpVotes', comment.ups)
        print('Comment Score', comment.score)
        print('Comment Submission', comment.submission)
        print('Comment User Reports', comment.user_reports)
        print('Comment Subreddit', comment.subreddit)
        print('Comment Post', comment.submission)
        print('Submission Title: ', submission.title)
        print('Submission Score: ', submission.score)
        writer.writerows(comment.id, comment.body)
        comment_queue.extend(comment.replies)

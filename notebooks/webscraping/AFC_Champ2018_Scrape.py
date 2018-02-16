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
game_thread_url = 'https://www.reddit.com/r/nfl/comments/7rzw8x/game_thread_jacksonville_jaguars_126_at_new/'
submission = reddit.submission(url=game_thread_url)
print("Number of Comments in Game Thread: {}".format(submission.num_comments))

# Pull Comments

submission.comments.replace_more(limit=None)
comment_queue = submission.comments[:]  # Seed with top-level

with open("AFC_Championship_Comments_2018.csv", "w") as output:
    writer = csv.writer(output, delimiter=',')
    column_headers = ['CommentID',
                      'DateTime',
                      'Time',
                      'Body',
                      'Author',
                      'Author_Flair',
                      'Author_Flair_CSS',
                      'Controversiality',
                      'Created',
                      'Depth',
                      'Score',
                      'Submission']
    writer.writerow([header for header in column_headers])
    count = 0
    while comment_queue:
        comment = comment_queue.pop(0)
        row = []

        # Created time
        mydatetime = datetime.datetime.fromtimestamp(comment.created_utc)
        mydate = mydatetime.strftime('%Y-%m-%d-%H:%M:%S')
        mytime = mydatetime.strftime('%H:%M:%S')

        # Parse Body
        body = comment.body.replace('\n',' ').replace(",",' ')
        print(str(comment.id))
        print(str(body))
        row.append(str(comment.id))
        row.append(mydate)
        row.append(mytime)
        row.append(str(body))
        row.append(str(comment.author))
        row.append(str(comment.author_flair_text))
        row.append(comment.author_flair_css_class)
        row.append(comment.controversiality)
        row.append(comment.created)
        row.append(comment.depth)
        row.append(comment.score)
        row.append(comment.submission)
        writer.writerows([row])
        comment_queue.extend(comment.replies)
        if count%1000 == 0:
            print("Count of prints {}".format(count))
        count += 1

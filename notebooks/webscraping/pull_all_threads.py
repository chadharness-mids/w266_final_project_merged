import praw
import pandas as pd
import configparser
import numpy as np
import datetime as dt
import pickle
import logging

logging.basicConfig(filename='pull_comments.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


# Setup Config for Reddit Data
# Store username/password data in reddit.config file
config = configparser.ConfigParser()
config.read('../reddit.config')

reddit = praw.Reddit(client_id=config['REDDIT_CONFIG']['client_id'],
                     client_secret=config['REDDIT_CONFIG']['client_secret'],
                     password=config['REDDIT_CONFIG']['password'],
                     user_agent=config['REDDIT_CONFIG']['user_agent'],
                     username=config['REDDIT_CONFIG']['username'])


def parse_comment(comment):
    try:
        author = comment.author.name
        author_flair = comment.author_flair_text
    except:
        author = 'None'
        author_flair = 'None'
    score = comment.score

    comment_id = comment
    comment_name = comment.name
    comment_fullname = comment.fullname
    comment_is_root = comment.is_root
    comment_parent = comment.parent()
    comment_approved_at_utc = comment.approved_at_utc
    comment_approved_by = comment.approved_by
    comment_created = comment.created
    comment_created_utc = comment.created_utc
    comment_created_utc_datetime = dt.datetime.fromtimestamp(comment.created_utc)
    comment_created_utc_date = comment_created_utc_datetime.strftime(format='%d-%m-%y')
    comment_created_utc_time = comment_created_utc_datetime.strftime(format='%H:%M:%S')
    comment_banned_at_utc = comment.banned_at_utc
    comment_banned_by = comment.banned_by
    comment_depth = comment.depth
    comment_num_reports = comment.num_reports
    comment_body = comment.body
    comment_body_parsed = comment.body.replace('\n',' ').replace('\t',' ').replace(',',' ')
    # Submission Details
    submission_id = comment.submission.id
    submission_title = comment.submission.title
    submission_created_utc = comment.submission.created_utc

    data = [author,
            author_flair,
            score,
            comment_id,
            comment_name,
            comment_fullname,
            comment_is_root,
            comment_parent,
            comment_approved_at_utc,
            comment_approved_by,
            comment_created,
            comment_created_utc,
            comment_created_utc_datetime,
            comment_created_utc_date,
            comment_created_utc_time,
            comment_banned_at_utc,
            comment_banned_by,
            comment_depth,
            comment_num_reports,
            comment_body,
            comment_body_parsed,
            submission_id,
            submission_title,
            submission_created_utc]

    return data

def pull_comments_and_save(submission_id):
    submission = reddit.submission(id=submission_id)
    game_comments = pd.DataFrame(columns=['author',
                                            'author_flair',
                                            'score',
                                            'comment_id',
                                            'comment_name',
                                            'comment_fullname',
                                            'comment_is_root',
                                            'comment_parent',
                                            'comment_approved_at_utc',
                                            'comment_approved_by',
                                            'comment_created',
                                            'comment_created_utc',
                                            'comment_created_utc_datetime',
                                            'comment_created_utc_date',
                                            'comment_created_utc_time',
                                            'comment_banned_at_utc',
                                            'comment_banned_by',
                                            'comment_depth',
                                            'comment_num_reports',
                                            'comment_body',
                                            'comment_body_parsed',
                                            'submission_id',
                                            'submission_title',
                                            'submission_created_utc'])
    logging.info("ROBSLOG Pulling Comments for Thread {} with {} Comments".format(submission.title, submission.num_comments))
    submission.comments.replace_more(limit=None)

    submission_pickle_filename = 'data/{}_submission_pickle.p'.format(submission_id)
    pickle.dump(submission,open( submission_pickle_filename, "wb" ))

    comment_queue = submission.comments[:]  # Seed with top-level
    comment_number = 1

    while comment_queue:
        comment = comment_queue.pop(0)
        try:
            data = parse_comment(comment)
            # Save Results
            game_comments.loc[comment_number] = data
        except:
            logging.warning('ROBSLOG Count pull comment{}'.format(comment))

        comment_queue.extend(comment.replies)
        comment_number += 1

    now = dt.datetime.now()
    logging.info("ROBSLOG Complete at: {}".format(now.strftime(format='%d-%m-%y %H:%M:%S')))
    return game_comments

games = pd.read_csv('Game_Thread_List_Only.csv')
games = games.sort_values('Number of Comments')
# threads = games['Thread ID'].tolist()

threads = ['7vad8n','7vb5tk']

for submissionid in threads:
    try:
        df = pull_comments_and_save(submissionid)
        df.to_csv('data/{}_parsed_comments.csv'.format(submissionid))
        df.to_pickle('data/{}_parsed_comments.pickle'.format(submissionid))
    except:
        logging.warning("ROBSLOG Pull for {} failed!!".format(submissionid))

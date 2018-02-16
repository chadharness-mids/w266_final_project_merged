#!/usr/bin/env python
# encoding: utf-8

import tweepy
import datetime as dt
from configparser import ConfigParser
import pandas as pd
import csv

config = ConfigParser()
config.read('twitter.conf')

usernames = ['cardinals_pbp',
    'bears_pbp',
    'packers_pbp',
    'giants_pbp',
    'lions_pbp',
    'redskins_pbp',
    'eagles_pbp',
    'steelers_pbp',
    'rams_pbp',
    '49ers_pbp',
    'browns_pbp',
    'colts_pbp',
    'cowboys_pbp',
    'chiefs_pbp',
    'chargers_pbp',
    'broncos_pbp',
    'jets_pbp',
    'patriots_pbp',
    'raiders_pbp',
    'titans_pbp',
    'bills_pbp',
    'vikings_pbp',
    'falcons_pbp',
    'dolphins_pbp',
    'saints_pbp',
    'bengals_pbp',
    'seahawks_pbp',
    'bucs_pbp',
    'panthers_pbp',
    'jaguars_pbp',
    'ravens_pbp',
    'texans_pbp']

def get_all_tweets(screen_name):
    #Twitter only allows access to a users most recent 3240 tweets with this method

    #authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key=config['TWITTER']['CONSUMER_KEY'],
            consumer_secret=config['TWITTER']['CONSUMER_SECRET'])
    auth.set_access_token(key=config['TWITTER']['ACCESS_TOKEN'],
            secret=config['TWITTER']['ACCESS_SECRET'])
    api = tweepy.API(auth)

    #initialize a list to hold all the tweepy Tweets
    alltweets = []

    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = screen_name,count=200)

    #save most recent tweets
    alltweets.extend(new_tweets)

    #save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

   #keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print("getting tweets before {}".format(oldest))

        #all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)

        #save most recent tweets
        alltweets.extend(new_tweets)

        #update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print("...{} tweets downloaded so far".format(len(alltweets)))

    #transform the tweepy tweets into a 2D array that will populate the csv
    outtweets = [[tweet.id_str,
                  tweet.created_at,
                  tweet.text.replace(',','').replace(';',''),
                  tweet.user.screen_name,
                  tweet.user.location,
                  tweet.user.time_zone,
                  tweet.source,
                  tweet.retweet_count,
                  tweet.favorite_count] for tweet in alltweets]

    #write the csv
    with open('{}_tweets.csv'.format(screen_name), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["id",
                         "created_at",
                         "text",
                         "screen_name",
                         "location",
                         "time_zone",
                         "source",
                         "retweet_count",
                         "favorite_count"])
        writer.writerows(outtweets)

    pass

for username in usernames:
    get_all_tweets(screen_name=username)

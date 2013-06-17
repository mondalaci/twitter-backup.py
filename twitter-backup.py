#!/usr/bin/env python

import os
import os.path
from sys import exit
import json
import oauth2 as oauth
from StringIO import StringIO
from urlparse import parse_qsl

# Please don't use this key and secret in your script.
# You can request your own at https://dev.twitter.com/apps/new
# (If you fork my repo to merely submit a pull request then you don't need to change this.)
consumer_key = 'I5Qy02p5CrIXw8Sa9ohw'
consumer_secret = 'ubG7dkIS6g2cjYshXM6gtN6dSZEekKTRZMKgjYIv4'

max_tweets_per_request = 200
access_token_filepath = '~/.config/twitter-backup.py/access-token.json'

def get_access_token_from_twitter():
    # Taken from https://github.com/simplegeo/python-oauth2#twitter-three-legged-oauth-example

    request_token_url = 'https://api.twitter.com/oauth/request_token'
    access_token_url = 'https://api.twitter.com/oauth/access_token'
    authorize_url = 'https://api.twitter.com/oauth/authorize'

    client = oauth.Client(consumer)

    # Step 1: Get a request token. This is a temporary token that is used for
    # having the user authorize an access token and to sign the request to obtain
    # said access token.

    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(parse_qsl(content))

    # Step 2: Redirect to the provider. Since this is a CLI script we do not
    # redirect. In a web application you would redirect the user to the URL
    # below.

    print "Visit %s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])

    # After the user has granted access to you, the consumer, the provider will
    # redirect you to whatever URL you have told them to redirect to. You can
    # usually define this in the oauth_callback argument as well.

    oauth_verifier = raw_input('What is the PIN? ')

    # Step 3: Once the consumer has redirected the user back to the oauth_callback
    # URL you can request the access token the user has approved. You use the
    # request token to sign this request. After this is done you throw away the
    # request token and use the access token returned. You should store this
    # access token somewhere safe, like a database, for future use.

    token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, "POST")
    access_token = dict(parse_qsl(content))

    if access_token == {}:
        print 'Invalid PIN was given'
        exit(1)

    return access_token

def fetch_tweets(access_token, max_id=None):
    token = oauth.Token(access_token['oauth_token'], access_token['oauth_token_secret'])
    client = oauth.Client(consumer, token)
    max_id = '' if max_id==None else '&max_id='+str(max_id)
    response = client.request('https://api.twitter.com/1.1/statuses/user_timeline.json?count=%d%s' % (max_tweets_per_request, max_id))
    response_headers, response_body = response
    tweets = json.load(StringIO(response_body))
    return tweets

def get_earliest_tweet_id(tweets):
    id = None
    for tweet in tweets:
        id = tweet['id']
    return id

def save_json(json_object, filepath):
    json_string = json.dumps(json_object, indent=4)
    with open(filepath, 'w') as file:
        file.write(json_string)

def save_access_token(token):
    token_directory = os.path.dirname(get_access_token_file_path())
    if not os.path.exists(token_directory):
        os.makedirs(token_directory)
    dumped_token = json.dumps(token)
    with open(get_access_token_file_path(), 'w') as file:
        file.write(dumped_token)

def load_access_token():
    try:
        with open(get_access_token_file_path(), 'r') as file:
            access_token = json.load(file)
        return access_token
    except IOError:
        return None

def get_access_token_file_path():
    return os.path.expanduser(access_token_filepath)

# Main program

consumer = oauth.Consumer(consumer_key, consumer_secret)

access_token = load_access_token()
if access_token == None:
    access_token = get_access_token_from_twitter()
    save_access_token(access_token)

earliest_tweet_id = None
page_number = 1
tweet_index = 0

while True:
    tweets = fetch_tweets(access_token, earliest_tweet_id)

    if len(tweets) > 0:
        dest_filename = '%02d.json' % (page_number)
        print 'Saving tweet %d to %d as %s' % (tweet_index, tweet_index+len(tweets), dest_filename)
        save_json(tweets, dest_filename)
        earliest_tweet_id = get_earliest_tweet_id(tweets)
        page_number += 1
        tweet_index += len(tweets)

    if len(tweets) < max_tweets_per_request:
        break

#!/usr/bin/env python

import oauth2 as oauth
from urlparse import parse_qsl
from os.path import expanduser
from sys import exit

consumer_key = 'I5Qy02p5CrIXw8Sa9ohw'
consumer_secret = 'ubG7dkIS6g2cjYshXM6gtN6dSZEekKTRZMKgjYIv4'

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

def fetch_tweets(access_token):
    token = oauth.Token(access_token['oauth_token'], access_token['oauth_token_secret'])
    client = oauth.Client(consumer, token);
    print client.request('https://api.twitter.com/1.1/statuses/home_timeline.json?count=200')

def save_access_token(token):
    pass

def load_access_token():
    pass

def get_access_token_file_path():
    return expanduser('~/.config/twitter-backup.py/access-token.json')

consumer = oauth.Consumer(consumer_key, consumer_secret)
access_token = get_access_token_from_twitter()
fetch_tweets(access_token)

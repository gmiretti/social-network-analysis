#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tweepy import Cursor, AppAuthHandler, OAuthHandler, API
from tweepy.error import TweepError
from random import choice
from localsettings import AUTH_DATA
from datetime import datetime
import time

# Used to switch between tokens to avoid exceeding rate limits
class APIHandler(object):
    """docstring for APIHandler"""
    def __init__(self, auth_data, max_nreqs=10):
        self.auth_data = auth_data
        self.index = choice(range(len(auth_data)))
        self.max_nreqs = max_nreqs
        self.get_fresh_connection()

    def conn(self):
        if self.nreqs == self.max_nreqs:
            self.get_fresh_connection()
        else:
            # print("Continuing with API Credentials #%d" % self.index)
            self.nreqs += 1
        return self.conn_

    def get_fresh_connection(self):
        success = False
        while not success:
            try:
                self.index = (self.index + 1) % len(self.auth_data)
                d = self.auth_data[self.index]
                print "Switching to API Credentials #%d" % self.index

                # auth = OAuthHandler(d['consumer_key'], d['consumer_secret'])
                # auth.set_access_token(d['access_token'], d['access_token_secret'])

                auth = AppAuthHandler(d['consumer_key'], d['consumer_secret'])
                self.conn_ = API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
                self.nreqs = 0
                return self.conn_
            except TweepError, e:
                print("Error trying to connect: %s" % e.message)
                time.sleep(10)

    def traer_seguidores(self, **kwargs):
        conns_tried = 0
        fids = []
        cursor = -1
        while cursor:
            try:
                fs, (_, cursor) = self.conn_.followers_ids(count=5000, cursor=cursor, **kwargs)
                fids += [str(x) for x in fs]
                # if not fids:
                #     # terminamos

                print "fetched %d followers so far." % len(fids)
            except TweepError, e:
                if not 'rate limit' in e.reason.lower():
                    raise e
                else:
                    conns_tried += 1
                    if conns_tried == len(self.auth_data):
                        nmins = 15
                        print e
                        print "Rate limit reached for all connections. Waiting %d mins..." % nmins
                        time.sleep(60 * nmins)
                        conns_tried = 0 # restart count
                    else:
                        self.get_fresh_connection()

        return fids

    def search(self, search_kw, **kwargs):
        conns_tried = 0
        tweets = []
        cursor = -1
        while cursor:
            try:
                tws, (_, cursor) = self.conn_.search(search_kw, count=100, cursor=cursor, **kwargs)
                tweets += tws
                # if not fids:
                #     # terminamos

                print "fetched %d tweets so far." % len(tweets)
            except TweepError, e:
                if not 'rate limit' in e.reason.lower():
                    raise e
                else:
                    conns_tried += 1
                    if conns_tried == len(self.auth_data):
                        nmins = 15
                        print e
                        print "Rate limit reached for all connections. Waiting %d mins..." % nmins
                        time.sleep(60 * nmins)
                        conns_tried = 0 # restart count
                    else:
                        self.get_fresh_connection()

        return tweets

    def traer_seguidos(self, **kwargs):
        conns_tried = 0
        fids = []
        cursor = -1
        while cursor:
            try:
                fs, (_, cursor) = self.conn_.friends_ids(count=5000, cursor=cursor, **kwargs)
                fids += [str(x) for x in fs]
                # print "fetched %d followers so far." % len(fids)
            except TweepError, e:
                if not 'rate limit' in e.reason.lower():
                    raise e
                else:
                    conns_tried += 1
                    if conns_tried == len(self.auth_data):
                        nmins = 15
                        print e
                        print "Rate limit reached for all connections. Waiting %d mins..." % nmins
                        time.sleep(60 * nmins)
                        conns_tried = 0 # restart count
                    else:
                        self.get_fresh_connection()

        return fids


    def traer_timeline(self, user_id, desde=None, hasta=None, dia=None, limite=None):
        page = 1
        tweets = []
        if dia:
            desde = dia
            hasta = dia

        while True:
            try:
                page_tweets = self.conn_.user_timeline(user_id=user_id, page=page)
                if not page_tweets:
                    break

                for tw in page_tweets: 
                    # print(tw.text)
                    if desde and tw.created_at.date() < desde:
                        break
                    if hasta and tw.created_at.date() > hasta:
                        continue                        

                    tweets.append(tw._json) # =dia or >= desde
                    if limite and len(tweets) >= limite:
                        break
                page += 1
            except Exception, e:                
                if e.message == u'Not authorized.':
                    break
                else:
                    print("Error: %s" % e.message)
                    print "waiting..."
                    time.sleep(30)
                    continue

        return tweets

API_HANDLER = APIHandler(AUTH_DATA)
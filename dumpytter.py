# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Shigemi ISHIDA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the Institute nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#

import sys
import rauth
import json
from datetime import datetime
from dateutil import parser as dt_parser
from dateutil import tz

import config
import database

#======================================================================
class Dumpytter():
    def __init__(self):
        # load config.
        self.conf = config.Config()
        if not self.conf.get():
            sys.stderr.write("Get twitter API tokens and create a config file."
                             "  See README.\n")
            del self.conf
            quit()

        # OAuth session.
        twitter = rauth.OAuth1Service(
            consumer_key=self.conf.consumer_key,
            consumer_secret=self.conf.consumer_sec,
            name="twitter",
            access_token_url="https://api.twitter.com/oauth/access_token",
            authorize_url="https://api.twitter.com/oauth/authorize",
            base_url="https://api.twitter.com/1.1/")
        self.conn = rauth.OAuth1Session(
            consumer_key=self.conf.consumer_key,
            consumer_secret=self.conf.consumer_sec,
            access_token=self.conf.access_token,
            access_token_secret=self.conf.access_sec,
            service=twitter)

        # create a DB instance.
        self.db = database.DataBase(self.conf.dbfile)

        return

    #--------------------------------------------------
    def __call__(self):
        raw_tweets = self.get_new_tweets_amap()
        if len(raw_tweets) == 0:
            # no new tweets
            sys.stderr.write("No new tweets.\n")
            return

        # extract required info.
        tweets = self.extract_info(raw_tweets)

        # store them to DB.
        self.store_to_db(tweets)

    #--------------------------------------------------
    def get_last_status_id(self):
        self.db.cur.execute("SELECT status_id FROM statuses ORDER BY status_id DESC LIMIT 1")
        res = self.db.cur.fetchone()
        if res is not None:
            ret = res.get("status_id", None)
        else:
            ret = None
        return ret

    #--------------------------------------------------
    def store_to_db(self, tweets):
        # an INSERT statement template.
        sql = ("INSERT INTO statuses"
               " (status_id, status_text, user_id, user_screen_name, status_reply,"
               " status_at, created_at, updated_at) VALUES"
               " (:status_id, :status_text, :user_id, :user_screen_name, :status_reply,"
               "  :status_at, :created_at, :updated_at)")

        for tweet in tweets:
            tweet["created_at"] = datetime.now()
            tweet["updated_at"] = datetime.now()
            # execute the sql
            try:
                self.db.cur.execute(sql, tweet)
            except Exception, detail:
                sys.stderr.write("Cannot insert into DB.  " + detail[0] + "\n")
                self.db.conn.rollback()
                return

        self.db.conn.commit()

        return

    #--------------------------------------------------
    # get new tweets as much as possible
    def get_new_tweets_amap(self):
        # retrieve last status_id.
        since_id = self.get_last_status_id()
        max_id = None

        # retrieve new tweets up to 3200 tweets.
        raw_tweets = []
        for cnt in range(0,16):
            # retrieve new tweets up to 200 tweets.
            #   API limits max number of tweet retrieval.
            tweets = self.get_tweets(since_id=since_id, max_id=max_id)
            # merge (newer first).
            raw_tweets.extend(tweets)

            # no more new tweets?
            if tweets is None or len(tweets) == 0:
                break

            # update max_id to retrieve old tweets
            max_id = tweets[-1]["id"] - 1

        return raw_tweets

    #--------------------------------------------------
    def get_tweets(self, since_id=None, max_id=None):
        params = {"count": 200}
        if since_id is not None:
            params["since_id"] =  since_id
        if max_id is not None:
            params["max_id"] = max_id
        tweets = self.conn.get(url="statuses/user_timeline.json",
                               params=params)

        # check HTTP status to return error when error.
        ret = None
        if tweets.ok:
            ret = json.loads(tweets.content)

        return ret

    #--------------------------------------------------
    def extract_info(self, raws):
        tweets = []
        # iterate to extarct required info.
        for raw in reversed(raws):
            # reply?
            if raw["in_reply_to_status_id"] is None:
                reply = False
            else:
                reply = True
            # convert to datetime with local timezone.
            status_at = dt_parser.parse(raw["created_at"]).astimezone(tz.tzlocal())
            tweets.append(
                {"status_id"        : raw["id"],
                 "status_text"      : raw["text"],
                 "user_id"          : raw["user"]["id"],
                 "user_screen_name" : raw["user"]["screen_name"],
                 "status_reply"     : reply,
                 "status_at"        : status_at})
        return tweets

    #--------------------------------------------------
    def __del__(self):
        del self.db
        del self.conf
        del self.conn
        return

#======================================================================
if __name__ == "__main__":
    dump = Dumpytter()
    dump()

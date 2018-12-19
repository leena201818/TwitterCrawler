# encoding=utf-8
import json
from pymongo import MongoClient
import datetime

class MongoHelper:
    def __init__(self):
        with open('config.json', 'r') as f:
            x = json.load(f)
            self._conn = MongoClient(host = x['mongoinfo']['dbIP'],port = int(x['mongoinfo']['dbPort']))
            self._db = self._conn.twitter
            self._db.authenticate(x['mongoinfo']['dbUser'], x['mongoinfo']['dbPwd'])

    def insertuser(self,users):
        for u in users:
            u.pop('status')
            u.pop('entities')
            u['_id'] = "twitter_userid_%s"%u['id']
            u['scrapped'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._db.users.save(u)

    def insertfriends(self,user_id,friends):
        friends['_id'] = "twitter_friends_%s_%s"%(user_id,friends['next_cursor'])
        friends['twid'] = user_id
        friends['relationtype'] = 'friends'
        friends['scrapped'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._db.user_relationships.save(friends)

    def inserttweets(self,user_id,tweet):
        tweet.pop('entities')
        tweet.pop('user')
        # tweet['_id'] = "twitter_tweets_%s"%(tweet['id'])
        tweet['twid'] = user_id
        tweet['posttype'] = "origin"    #origin,like,retweet
        tweet['scrapped'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._db.tweets.save(tweet)

if __name__ == '__main__':
    # with open('./data/users_by_screen_names/20180524044036','r') as f:
    #     users = json.load(f)
    #     MongoHelper().insertuser(users)

    with open('./data/friends_ids/1561123663','r') as f:
        friends = json.load(f)
        MongoHelper().insertfriends('1',friends)
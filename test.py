# encoding=utf-8
import json

def getDispatchServerConfig():
    with open('config.json', 'r') as f:
        x = json.load(f)
        return x['serverinfo']['serverIP'], x['serverinfo']['serverPort']

if __name__ == '__main__':
    x = getDispatchServerConfig()
    print(x)

    # from mongohelper import MongoHelper
    # m = MongoHelper()
    # u = [{'id':1,'name':'kevin','status':'','entities':''}]
    # m.insertuser(u)

    from twython import Twython

    # APP_KEY = "pgplvZFXMYtx494iQD2UhXwat"
    # APP_SECRET = '9dzDzuXmvyKfwQCspBTE6FBRiMmvN2MB3TytcPFpUa1olxdkMu'
    # OAUTH_TOKEN = '984036369688354816zZjZo2nFvh1XsWNORuS4NdAQturWFzl'
    # OAUTH_TOKEN_SECRET = 'vxNnvyY3ijBToVMwTowJiHZ4soNcuuRq66CgUGHr3AL4E'

    APP_KEY = "4ekFQ"
    APP_SECRET = 'LScQAuQXulguFL7YYCXhuo'
    OAUTH_TOKEN = '9186391TChLZS6V'
    OAUTH_TOKEN_SECRET = 'Avp1jZkd'


    twitter = Twython(APP_KEY, APP_SECRET,OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    t = twitter.get_home_timeline()
    print(t)

    # twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
    # ACCESS_TOKEN = twitter.obtain_access_token()
    # twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
    # t = twitter.get_home_timeline()

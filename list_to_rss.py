import tweepy
from feedgen.feed import FeedGenerator
import os
import urllib
import sys
import config
# reload(sys)
# sys.setdefaultencoding('utf8')

ConsumerKey = config.twitter['ConsumerKey']
ConsumerSecret = config.twitter['ConsumerSecret']
AccessToken = config.twitter['AccessToken']
AccessTokenSecret = config.twitter['AccessTokenSecret']
twitterName = config.twitter['twitterName']
rssFeedDir = config.rssFeedDir

auth = tweepy.OAuthHandler(ConsumerKey, ConsumerSecret)
auth.set_access_token(AccessToken,AccessTokenSecret)
api = tweepy.API(auth)

name=config.name
email=config.email
get_me_lists=config.getMeLists

link=config.link
count=config.count
for lista in get_me_lists:
    print lista
    fg = FeedGenerator()
    fg.id(link+lista+'.xml')
    fg.title('twitter '+lista)
    fg.author( {'name':name,'email':email} )
    fg.link( href=link, rel='alternate' )
    fg.description(lista)

    public_tweets = api.list_timeline(twitterName,lista,count=count)
    for tweet in public_tweets:
        fe = fg.add_entry()
        fe.id('https://twitter.com/'+tweet.user.screen_name+'/status/'+str(tweet.id)+'')
        fe.title(tweet.user.screen_name)
        fe.link( href='https://twitter.com/'+tweet.user.screen_name+'/status/'+str(tweet.id)+'', rel='alternate' )
        fe.description(u''+tweet.text)
        fe.author( {'name':tweet.user.screen_name,'email':email} )
    fg.rss_file(rssFeedDir+lista+'.xml',pretty=True,encoding='UTF-8', xml_declaration=True)

#print api.rate_limit_status()

import tweepy
from feedgen.feed import FeedGenerator
import os
import urllib
import sys
import config
import urllib2
from lxml import html
from collections import defaultdict
import ssl
from tinydb import TinyDB, Query

db = TinyDB('db.json')

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


def getTwitterCard(url):
    context = ssl._create_unverified_context()
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
    req = urllib2.Request(url, headers=hdr)

    doc   = html.parse(urllib2.urlopen(req, context=context))
    data  = defaultdict(dict)
    props = doc.xpath('//meta[re:test(@name|@property, "^twitter|og:.*$", "i")]',namespaces={"re": "http://exslt.org/regular-expressions"})
    packMe = {}
    packMe2 = []
    for prop in props:
        if prop.get('property'):
            key = prop.get('property').split(':')
        else:
            key = prop.get('name').split(':')

        if prop.get('content'):
            value = prop.get('content')
        else:
            value = prop.get('value')

        if not value:
            continue
        value = value.strip()

        if value.isdigit():
            value = int(value)
        key.pop(0)
        if key[0]=='description':
            packMe['description']=value
        if key[0]=='image':
            if 'http' in str(value):
                packMe['image']='<img src="'+value+'">'
    for value in packMe:
        packMe2.append(packMe[value])
    return packMe2

for lista in get_me_lists:
    fg = FeedGenerator()
    fg.id(link+lista+'.xml')
    fg.title('twitter1 '+lista)
    fg.author( {'name':name,'email':email} )
    fg.link( href=link, rel='alternate' )
    fg.description(lista)

    public_tweets = api.list_timeline(twitterName,lista,count=count)
    for tweet in public_tweets:
        Ids = Query()
        ex  = db.search(Ids.id == tweet.id)
        if len(ex)==0:
            print "new rss"
            pm = ""
            if len(tweet.entities['urls'])>0:
                try:
                    packMe = getTwitterCard(tweet.entities['urls'][0]['expanded_url'])
                    if isinstance(packMe, list):
                        pm= "".join(packMe)
                except Exception as e:
                    print e 

            media_url=""
            if  tweet.entities.has_key('media'):
                media_url= '<img src="'+tweet.entities['media'][0]['media_url_https']+'"><br/>'
            im='<img src="'+tweet._json['user']['profile_image_url']+'"><br/>'
            fe = fg.add_entry()
            fe.id('https://twitter.com/'+tweet.user.screen_name+'/status/'+str(tweet.id)+'')
            fe.title(tweet.user.screen_name)
            fe.link( href='https://twitter.com/'+tweet.user.screen_name+'/status/'+str(tweet.id)+'', rel='alternate' )
            fe.description(u''+im+tweet.text+media_url+"<br/>"+pm)
            fe.author( {'name':tweet.user.screen_name,'email':email} )
            db.insert({'id': tweet.id,"pm":pm})
        else:
            print "already ready rss"
            media_url=""
            if  tweet.entities.has_key('media'):
                media_url= '<img src="'+tweet.entities['media'][0]['media_url_https']+'"><br/>'
            im='<img src="'+tweet._json['user']['profile_image_url']+'"><br/>'
            fe = fg.add_entry()
            fe.id('https://twitter.com/'+tweet.user.screen_name+'/status/'+str(tweet.id)+'')
            fe.title(tweet.user.screen_name)
            fe.link( href='https://twitter.com/'+tweet.user.screen_name+'/status/'+str(tweet.id)+'', rel='alternate' )
            fe.description(u''+im+tweet.text+media_url+"<br/>"+ex[0]['pm'])
            fe.author( {'name':tweet.user.screen_name,'email':email} )
    rssfeed  = fg.rss_str(pretty=True)
    fg.rss_file(rssFeedDir+lista+'.xml',pretty=True,encoding='UTF-8', xml_declaration=True)

#print api.rate_limit_status()

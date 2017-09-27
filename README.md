### Convert twitter lists to rss feed.

```
sudo pip install -r requirements.txt
```

Edit config.py
```
twitter = dict(
    ConsumerKey         = 'xxxx',
    ConsumerSecret      = 'xxxxx',
    AccessToken         = 'xxxx-xxxxx',
    AccessTokenSecret   = 'xxxxxxxx',
    twitterName         = 'myname'
)
rssFeedDir = '/usr/local/var/www/'
link        =   'http://xxx.me:8080/'
name        =   "myname"
email       =   "myname@x.me"
getMeLists  =   ['tech','funny']
count       =   50 #200 max

```

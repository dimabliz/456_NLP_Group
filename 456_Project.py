from nltk.twitter import Query, Streamer, Twitter, TweetViewer, TweetWriter, credsfromfile
import tweepy

def pre_process_words(tweet_words):
    for item in list(tweet_words):
        if item.count == 0:
            tweet_words.remove(item)

        for word in list(item):
            if word.startswith("http"):
                item.remove(word)

        if item[0] == "RT":
            item.remove("RT")

        if item.count == 0:
            tweet_words.remove(item)

def main():

    #export TWITTER="/path/to/twitter-files"
    #export TWITTER="/Users/dima/twitter-files"


    oauth = credsfromfile()
    auth = tweepy.OAuthHandler(oauth.get('app_key'), oauth.get('app_secret'))
    auth.set_access_token(oauth.get('oauth_token'), oauth.get('oauth_token_secret'))
    api = tweepy.API(auth)
    seattleID = 2490383
    trends = api.trends_place(seattleID)
    trendNames = [trend['name'] for trend in trends[0]['trends']]
    print(trendNames)
    
    client = Query(**oauth)
    print("\nCurrent Trend: %s\n" % trendNames[44])
    tweets = client.search_tweets(keywords=trendNames[44], limit=10)
    

    tweet_text = []

    for tweet in tweets:
        if tweet['lang'] == "en":
            tweet_text.append(tweet['text'])

    #list of list of tweet words
    tweet_words = []

    for i in tweet_text:
        tweet_words.append(i.split())

    pre_process_words(tweet_words)

    for i in tweet_words:
        print(i)
        print()

if __name__ == "__main__":
    main()

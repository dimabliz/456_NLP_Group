import nltk
from nltk.twitter import Query, Streamer, Twitter, TweetViewer, TweetWriter, credsfromfile
from nltk.sentiment.vader import SentimentIntensityAnalyzer
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

        if item[0].startswith("@"):
            item.remove(item[0])

        if item.count == 0:
            tweet_words.remove(item)

def get_final_tweet_sents(processed_tweet_sents, num_of_tweets):
    oauth = credsfromfile()
    auth = tweepy.OAuthHandler(oauth.get('app_key'), oauth.get('app_secret'))
    auth.set_access_token(oauth.get('oauth_token'), oauth.get('oauth_token_secret'))
    api = tweepy.API(auth)

    # Retrieve the WOEID (Where on Earth ID) for Seattle
    seattleID = 0
    for trend in api.trends_available():
        if (trend['name'] == 'Seattle'):
            seattleID = trend['woeid']

    # Retrieve the current trends in Seattle
    trends = api.trends_place(seattleID)
    trendNames = [trend['name'] for trend in trends[0]['trends']]
    print(trendNames)

    client = Query(**oauth)
    print("\nCurrent Trend: %s\n" % trendNames[0])
    tweets = client.search_tweets(keywords=trendNames[0], limit=num_of_tweets)

    tweet_text = []

    for tweet in tweets:
        if tweet['lang'] == "en":
            tweet_text.append(tweet['text'])

    # list of list of tweet words
    tweet_words = []

    for i in tweet_text:
        tweet_words.append(i.split())

    pre_process_words(tweet_words)

    #processed_tweet_sents = []

    for i in tweet_words:
        processed_tweet_sents.append(" ".join(i))

    # print("processed sents")
    # for i in processed_tweet_sents:
    #     print(i)


def main():

    #export TWITTER="/path/to/twitter-files"

    # oauth = credsfromfile()
    # auth = tweepy.OAuthHandler(oauth.get('app_key'), oauth.get('app_secret'))
    # auth.set_access_token(oauth.get('oauth_token'), oauth.get('oauth_token_secret'))
    # api = tweepy.API(auth)
    #
    # # Retrieve the WOEID (Where on Earth ID) for Seattle
    # seattleID = 0
    # for trend in api.trends_available():
    #     if (trend['name'] == 'Seattle'):
    #        seattleID = trend['woeid']
    #
    # # Retrieve the current trends in Seattle
    # trends = api.trends_place(seattleID)
    # trendNames = [trend['name'] for trend in trends[0]['trends']]
    # print(trendNames)
    #
    # client = Query(**oauth)
    # print("\nCurrent Trend: %s\n" % trendNames[0])
    # tweets = client.search_tweets(keywords=trendNames[0], limit=10)
    #
    #
    # tweet_text = []
    #
    # for tweet in tweets:
    #     if tweet['lang'] == "en":
    #         tweet_text.append(tweet['text'])
    #
    # #list of list of tweet words
    # tweet_words = []
    #
    # for i in tweet_text:
    #     tweet_words.append(i.split())
    #
    # pre_process_words(tweet_words)
    #
    # processed_tweet_sents = []
    #
    # for i in tweet_words:
    #     processed_tweet_sents.append(" ".join(i))
    #
    # print("processed sents")
    # for i in processed_tweet_sents:
    #     print(i)

    processed_tweet_sents = []
    get_final_tweet_sents(processed_tweet_sents, 10)
    print("processed sents")
    for i in processed_tweet_sents:
        print(i)

if __name__ == "__main__":
    main()

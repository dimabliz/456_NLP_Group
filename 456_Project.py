

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

    from nltk.twitter import Query, Streamer, Twitter, TweetViewer, TweetWriter, credsfromfile
    oauth = credsfromfile()

    client = Query(**oauth)
    tweets = client.search_tweets(keywords='arsenal', limit=10)

    # tweet = next(tweets)
    # from pprint import pprint
    # pprint(tweet, depth=1)

    tweet_text = []

    for tweet in tweets:
        if tweet['lang'] == "en":
            #print(tweet['text'])
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

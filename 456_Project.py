from nltk.twitter import Query, Streamer, Twitter, TweetViewer, TweetWriter, credsfromfile
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import tweepy

def getTopTrends(name, oauth, totalTrends):
    auth = tweepy.OAuthHandler(oauth.get('app_key'), oauth.get('app_secret'))
    auth.set_access_token(oauth.get('oauth_token'), oauth.get('oauth_token_secret'))
    api = tweepy.API(auth)
    ID = 0
    for trend in api.trends_available():
        if (trend['name'] == name and trend['countryCode'] == 'US'):
            ID = trend['woeid']
    trends = api.trends_place(ID)
    trendNames = [trend['name'] for trend in trends[0]['trends'][0:totalTrends]]
    return trendNames

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

def get_final_tweet_sents(num_of_tweets, trend, client):
    processed_tweet_sents = []
    
    tweets = client.search_tweets(keywords=trend, limit=num_of_tweets)

    tweet_text = []

    for tweet in tweets:
        if tweet['lang'] == "en":
            tweet_text.append(tweet['text'])

    # list of list of tweet words
    tweet_words = []
    for i in tweet_text:
        tweet_words.append(i.split())
    
    pre_process_words(tweet_words)

    for i in tweet_words:
        processed_tweet_sents.append(" ".join(i))
        
    return processed_tweet_sents

     

def main():
    oauth = credsfromfile()
    analyser = SentimentIntensityAnalyzer()
    # Retrieve the WOEID (Where on Earth ID) for Seattle
    #city = "Seattle"
    cities = ["Seattle"]
    
    totalTrends = 10
    numTweets = 100
    # Retrieve the top trends in Seattle
    for city in cities:
        print("Current City:", city)
        trends = getTopTrends(city, oauth, totalTrends)
        for trend in trends:
            client = Query(**oauth)
            print("\nCurrent Trend: %s\n" % trend)
            
            tweets = get_final_tweet_sents(numTweets, trend, client)
            totals = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
            for tweet in tweets:
                 sentiment = analyser.polarity_scores(tweet)
                 #print("{:-<40} {}".format(tweet, str(sentiment)))
                 if (sentiment['compound'] > 0 and sentiment['pos'] > 0):
                     totals['Positive'] += 1
                     #print("This tweet was positive!\n")
                 elif (sentiment['compound'] < 0 and sentiment['neg'] > 0):
                     totals['Negative'] += 1
                     #print("This tweet was negative!\n")
                 elif (sentiment['neu'] == 1):
                     totals['Neutral'] += 1
                     #print("This tweet was neutral!\n")
            opinions = []
            num = max(totals.values())
            
            for sent in totals.keys():
                if totals[sent] == num:
                    opinions.append(sent)
                    
            if len(opinions) == 1:
                print("Opinion for the topic {}: {} with {} out of {} tweets.".format
                (trend, opinions[0], num, numTweets))
            else:
                print("Opinions for the topic {}: split between ".format(trend), end = "")
                for i in range(len(opinions)):
                    print(opinions[i], end = "")
                    if (i != len(opinions)-1):
                        print(", ", end = "")
                    else:
                        print(" ", end = "")
                print("with {} out of {} tweets".format(num, numTweets))
            #totals = {}
            
        

if __name__ == "__main__":
    main()

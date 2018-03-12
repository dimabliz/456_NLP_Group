from nltk.twitter import Query, Streamer, Twitter, TweetViewer, TweetWriter, credsfromfile
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import tweepy

MAXTRENDS = 5
MAXTWEETS = 100
    
def getTopTrends(name, api):
    ID = 0
    for trend in api.trends_available():
        if (trend['name'] == name):
            ID = trend['woeid']
    trends = api.trends_place(ID)
    trendNames = [trend['name'] for trend in trends[0]['trends'][0:MAXTRENDS]]
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

def get_final_tweet_sents(trend, client):
    processed_tweet_sents = []
    
    tweets = client.search_tweets(keywords=trend, limit=MAXTWEETS)

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

#gets user input 
def get_user_input(options):
    entry = input("Enter 1 for trends of the US: \n" 
                  + "Enter 2 for trends of Seattle: \n"
                  + "Enter 3 for trends of a city in the US: \n")
    selection = []
    if entry == '1':
         print('<US>')
         selection = ["United States"]
    elif entry == '2':
        print('<Seattle>')
        selection = ['Seattle']
    elif entry == '3':
        print('<City>')
        city = input("Enter a city name from the following options: {}\n".format(options))
        selection = [city]
        while selection[0] not in options:
            selection[0] = input("Enter a valid city name.\n")
    
    return selection

def getOpinion(selection, oauth, api):
   
    analyser = SentimentIntensityAnalyzer()
    for name in selection:
        trends = getTopTrends(name, api)
        for trend in trends:
            client = Query(**oauth)
            print("\nCurrent Trend: %s\n" % trend)
            
            tweets = get_final_tweet_sents(trend, client)
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
                (trend, opinions[0], num, MAXTWEETS))
            else:
                print("Opinions for the topic {}: split between ".format(trend), end = "")
                for i in range(len(opinions)):
                    print(opinions[i], end = "")
                    if (i != len(opinions)-1):
                        print(", ", end = "")
                    else:
                        print(" ", end = "")
                print("with {} out of {} tweets".format(num, MAXTWEETS))

def main():
    oauth = credsfromfile()
    auth = tweepy.OAuthHandler(oauth.get('app_key'), oauth.get('app_secret'))
    auth.set_access_token(oauth.get('oauth_token'), oauth.get('oauth_token_secret'))
    api = tweepy.API(auth)
    options = []
    for trend in api.trends_available():
        if (trend['countryCode'] == 'US' and trend['name'] != 'United States'):
            options.append(trend['name'])
    inp = get_user_input(options)
    api = tweepy.API(auth)
    getOpinion(inp, oauth, api)
    
if __name__ == "__main__":
    main()

from nltk.twitter import Query, credsfromfile
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import tweepy
FAVE_RATIO = 0.001
RETWEET_RATIO = 0.0001
FOLLOWERS_RATIO = 0.00001

def getTopTrends(totalTrends, name, api):
    ID = 0
    for trend in api.trends_available():
        if (trend['name'] == name):
            ID = trend['woeid']
    trends = api.trends_place(ID)
    trendNames = [trend['name'] for trend in trends[0]['trends'][0:totalTrends]]
    return trendNames

def pre_process_words(tweet_words):
    for item in list(tweet_words):
        for word in list(item):
            if word.startswith("http"):
                item.remove(word)

        if item[0] == "RT":
            item.remove("RT")

        if item[0].startswith("@"):
            item.remove(item[0])

def preprocess_tweet(raw_tweets):
    tweet_text = []
    processed_tweet_sents = []
    retweet_counts = []
    fave_counts = []
    followers_counts = []

    i = 0
    for tweet in raw_tweets:
        i+=1
        #if i<2:
        #    print(tweet)
        if tweet['lang'] == "en":
            tweet_text.append(tweet['text'])
            retweet_counts.append(tweet['retweet_count'])
            fave_counts.append(tweet['favorite_count'])
            followers_counts.append(tweet['user']['followers_count'])

    # list of list of tweet words
    tweet_words = []
    for i in tweet_text:
        tweet_words.append(i.split())

    pre_process_words(tweet_words)

    for i in tweet_words:
        processed_tweet_sents.append(" ".join(i))

    return processed_tweet_sents, retweet_counts, fave_counts, followers_counts

#gets user input
def get_user_input(options):
    invalid = 1
    while(invalid):
        entry = input("Enter 1 for trends of the US: \n"
                      + "Enter 2 for trends of Seattle: \n"
                      + "Enter 3 for trends of a city in the US: \n")
        selection = []
        if entry == '1':
             print('<US>')
             selection = "United States"
             invalid = 0
        elif entry == '2':
            print('<Seattle>')
            selection = 'Seattle'
            invalid = 0
        elif entry == '3':
            print('<City>')
            city = input("Enter a city name from the following options: {}\n".format(options))
            selection = city
            while selection not in options:
                selection = input("Enter a valid city name:\n")
            invalid = 0
        else:
            print("Invalid selection. Try again.")
    notInt = 1
    while(notInt):
        totalTrends = input("Enter the number of trends you would like to have. Pick a number between 0 and 30:\n")
        try:
            totalTrends = int(totalTrends)
        except ValueError:
            print("That's not an integer, try again")
        else:
            if totalTrends > 0 and totalTrends <= 30:
                notInt = 0
            else:
                print("Enter a total between 0 and 30.")

    return totalTrends, selection

def getOpinionTotals(tweets, retweet_counts, fave_counts, followers_count):
    analyser = SentimentIntensityAnalyzer()
    totals = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    sentiments = []
    for i in range(len(tweets)):
        sentiment = analyser.polarity_scores(tweets[i])
        sentiments.append(sentiment)

        if (sentiment['compound'] > 0 and sentiment['pos'] > 0):
                  totals['Positive'] += (1 +
                  RETWEET_RATIO * retweet_counts[i] +
                  FAVE_RATIO * fave_counts[i] +
                  FOLLOWERS_RATIO * followers_count[i])

        elif (sentiment['compound'] < 0 and sentiment['neg'] > 0):
                  totals['Negative'] += (1 +
                  RETWEET_RATIO * retweet_counts[i] +
                  FAVE_RATIO * fave_counts[i] +
                  FOLLOWERS_RATIO * followers_count[i])

        elif (sentiment['neu'] == 1):
                  totals['Neutral'] += (1 +
                  RETWEET_RATIO * retweet_counts[i] +
                  FAVE_RATIO * fave_counts[i] +
                  FOLLOWERS_RATIO * followers_count[i])

    return sentiments, totals

def getOpinionsOfTopic(topic, oauth, num_of_tweets):
    raw_tweets = []
    client = Query(**oauth)
    tweets = client.search_tweets(keywords=topic, limit=num_of_tweets)
    for tweet in tweets:
        raw_tweets.append(tweet)
    tweets, retweet_counts, fave_counts, followers_count = preprocess_tweet(raw_tweets)
    sentiments, totals = getOpinionTotals(tweets, retweet_counts, fave_counts, followers_count)

    adjustedTotal = totals['Positive'] + totals['Negative'] + totals['Neutral']
    posPercent = totals['Positive'] / adjustedTotal
    negPercent = totals['Negative'] / adjustedTotal
    neuPercent = totals['Neutral'] / adjustedTotal
    print("Opinions for the topic \"{}\":\nPositive: {:.0%}, Negative: {:.0%}, Neutral: {:.0%} out of {} tweets.\n"
                  .format(topic, posPercent, negPercent, neuPercent, num_of_tweets))

    greatestTotal = float(max(totals.values()))
    opinion = ""
    for key in totals.keys():
        if totals[key] == greatestTotal:
            opinion = key.lower()
    if opinion != 'Neutral'.lower():
        print("The topic was mostly {}. Finding the most {} tweet.".format(opinion, opinion))
    else:
        print("The topic was mostly neutral. Unable to find the most neutral tweet.")

    sent = {'pos' : 0, 'neg' : 0,'neu' : 0, 'compound' : 0}
    sentTweet = ""
    for i in range(len(tweets)):
        if opinion == 'Positive'.lower():
            if (sentiments[i]['compound'] >= sent['compound'] and sentiments[i]['pos'] > sent['pos']):
                sent = sentiments[i]
                sentTweet = raw_tweets[i]
        elif opinion == 'Negative'.lower():
            if (sentiments[i]['compound'] <= sent['compound'] and sentiments[i]['neg'] > sent['neg']):
                sent = sentiments[i]
                sentTweet = raw_tweets[i]

    if opinion != 'Neutral'.lower():
        print("Most {} tweet: {}".format(opinion, sentTweet['text']))
        print("URL: https://twitter.com/statuses/{}".format(sentTweet['id']))
    print("------------------------------------")

# Prompts the user to enter the number of tweets to analyze and re prompt if the
# number is not in range or if the input is not a number
def Number_of_Tweets():
    notInt = 1
    while (notInt):
        num_of_tweets = input("Enter the number of tweets you want to analyze:\n")
        try:
            num_of_tweets = int(num_of_tweets)
        except ValueError:
            print("That's not an integer, try again")
        else:
            if num_of_tweets > 0 and num_of_tweets <= 500:
                notInt = 0
            else:
                print("Enter a total between 0 and 500.")
    return num_of_tweets

def main():
    oauth = credsfromfile()
    print('Welcome to our Twitter Sentiment Analyzer!')
    keyword = ""
    invalid = 1
    while(invalid):
        entry = input("Enter 1 to search a topic: \n"
                      + "Enter 2 to analyze trends: \n")
        if entry == '1':
            while keyword == "" or keyword == " ":
                keyword = input("Enter a keyword or hashtag to search: ")

            num_of_tweets = Number_of_Tweets()

            getOpinionsOfTopic(keyword, oauth, num_of_tweets)
            invalid = 0

        elif entry == '2':
            auth = tweepy.OAuthHandler(oauth.get('app_key'), oauth.get('app_secret'))
            auth.set_access_token(oauth.get('oauth_token'), oauth.get('oauth_token_secret'))
            api = tweepy.API(auth)

            options = []
            for trend in api.trends_available():
                if (trend['countryCode'] == 'US' and trend['name'] != 'United States'):
                    options.append(trend['name'])

            totalTrends, location = get_user_input(options)
            trends = getTopTrends(totalTrends, location, api)

            num_of_tweets = Number_of_Tweets()

            for trend in trends:
                getOpinionsOfTopic(trend, oauth, num_of_tweets)
            invalid = 0
        else:
            print("Invalid Selection. Try again.")

if __name__ == "__main__": main()

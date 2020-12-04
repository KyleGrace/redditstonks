'''
This is a tool looking at 5 years of r/wallstreetbets data to see if the overall
sentiment of posts made can be used as a predictive tool for stock prices.

We will be looking at Starbucks, Google, Apple, Facebook, Tesla, Netflix, and SPY as they are
popular stocks with large market caps. 

'''
import math
import json
import csv
from datetime import datetime,timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyser = SentimentIntensityAnalyzer()

text_to_ticker = {
    "sbux" : "SBUX",
    "starbucks" : "SBUX",
    "google" : "GOOGL",
    "goog" : "GOOGL",
    "googl" : "GOOGL",
    "facebook" : "FB",
    "fb" : "FB",
    "apple" : "AAPL",
    "aapl" : "AAPL",
    "tesla" : "TSLA",
    "tsla" : "TSLA",
    "spy" : "SPY",
    "sp500" : "SPY",
    "netflix" : "NFLX",
    "nflx" : "NFLX",
}

ticker_to_index = {
    "SBUX": 0,
    "GOOGL" : 1,
    "TSLA" : 2,
    "AAPL" : 3,
    "SPY" : 4,
    "NFLX" : 5,
    "FB" : 6,
}

tickers = ["SBUX","GOOGL","TSLA","AAPL","SPY","NFLX","FB","Overall"]



def main():

    # day represented by current line
    current_line_day = None
    # day represented by previous line
    prev_line_day = None

    # daily aggregate sentiment scores for each stock, along with an overall score for ALL posts
    scores = [0,0,0,0,0,0,0,0]

    count = 0

    with open('investing_submission.json') as f, open("InvestingSentimentLog.csv",'w') as csvfile:
        csvwriter = csv.writer(csvfile)

        header = ["Date"] + tickers
        csvwriter.writerow(header)
        
        # go through each line of the file
        for line in f:
            # parsing json
            post = json.loads(line)
            time = post['created_utc']

            #converting from Unix time to datetime
            converted_time = datetime.utcfromtimestamp(time)

            # get us to the next trading day
            converted_time = next_weekday(converted_time)

            #generate a readble time
            human_time = converted_time.strftime('%m-%d-%Y')
            current_line_day = human_time



            #write to csv when we see new day
            if (prev_line_day != None) and (prev_line_day != current_line_day):

                # write to csv
                nextLine = [human_time] + scores
                csvwriter.writerow(nextLine)
                # reset scores
                scores = [0,0,0,0,0,0,0,0]
            
            prev_line_day = human_time

            keys = post.keys()

            # access content of post
            text = ""
            strings = []

            if 'selftext' in keys:
                strings.append(post['selftext'])
            if 'title' in keys:
                strings.append(post['title'])
            text = "".join(strings)

            # calculate sentiment score using VADER
            score = analyser.polarity_scores(text)['compound']

            #upvotes
            postscore = post['score']
            if postscore > 0:
                postscore = math.log(postscore)

            # weight each score by log(upvotes)
            weighted_score = score*postscore

            # add to overall sentiment 
            scores[7] += weighted_score

            # find ticker
            tick = find_ticker(text)

            if tick is not None:
                ind = ticker_to_index[tick]
                scores[ind] += weighted_score
                
            #counting lines
            count += 1
            if count % 10000 == 0:
                print(count, " Lines Processed")

        print(count, " Lines Processed")
        print("Finished Analysis")


            

def find_ticker(text):
    ''' finds the ticker given our set of interested tickers '''
    text = text.lower()
    for key in text_to_ticker.keys():
        if key in text:
            return text_to_ticker[key]
    return None


def next_weekday(time):
    ''' takes in datetime object and returns the next weekday'''
    if time.weekday() == 6:
        return time + timedelta(days=1)
    elif time.weekday() == 5:
        return time + timedelta(days=2)
    else:
        return time


if __name__ == "__main__":
    main()

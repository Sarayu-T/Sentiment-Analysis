import praw
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from textblob import TextBlob
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
user_agent = os.getenv('USER_AGENT')

# Initialize Reddit instance
reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)

def get_sentiment(text):
    try:
        analysis = TextBlob(text)
        return analysis.sentiment.polarity
    except:
        return 0

def analysisOfSubreddit(subreddit_name, time_filter):
    subreddit = reddit.subreddit(subreddit_name)
    posts = subreddit.top(time_filter=time_filter, limit=1000)  

    posts_data = []
    for post in posts:
        posts_data.append({
            'title': post.title,
            'score': post.score,
            'created': datetime.fromtimestamp(post.created_utc),
            'num_comments': post.num_comments,
            'upvote_ratio': post.upvote_ratio
        })

    df = pd.DataFrame(posts_data)
    print(df)

    df['sentiment'] = df['title'].apply(get_sentiment)
    df.set_index('created', inplace=True)

    sentiment_over_time = df['sentiment'].resample('M').mean()

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=sentiment_over_time)
    plt.title('Sentiment Over Time in r/{}'.format(subreddit_name))
    xlab = "Time(one "+ time_filter+")"
    plt.xlabel(xlab)
    plt.ylabel('Average Sentiment')
    plt.show()

    rolling_mean = sentiment_over_time.rolling(window=3).mean()
    rolling_std = sentiment_over_time.rolling(window=3).std()
    significant_changes = (sentiment_over_time - rolling_mean).abs() > 2 * rolling_std

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=sentiment_over_time, label='Sentiment')
    sns.scatterplot(data=sentiment_over_time[significant_changes], color='red', label='Significant Change')
    plt.title('Significant Sentiment Changes in r/{}'.format(subreddit_name))
    plt.xlabel(xlab)
    plt.ylabel('Average Sentiment')
    plt.legend()
    plt.show()

subr = input("Enter the subreddit: ")
time_filter = input("Enter the time frame (e.g., 'year', 'month'): ")
analysisOfSubreddit(subr, time_filter)

from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
from textblob import TextBlob

extractor = URLExtract()

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]

    num_messages = df.shape[0]
    total_words = sum(len(msg.split()) for msg in df['Message'])
    media_count = df['Message'].str.contains('<Media omitted>').sum()

    links = []
    for msg in df['Message']:
        links.extend(extractor.find_urls(msg))
    link_count = len(links)

    return num_messages, total_words, media_count, link_count

def most_busy_users(df):
    x = df['Sender'].value_counts().head()

    percent_df = (df['Sender'].value_counts(normalize=True) * 100).round(2) \
        .reset_index().rename(columns={'index': 'User', 'Sender': 'Percent'})

    return x, percent_df

def create_wordcloud(selected_user, df):
    with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
        stop_words = f.read().splitlines()

    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]

    temp = df[df['Sender'] != 'group_notification']
    temp = temp[temp['Message'] != '<Media omitted>\n'].copy()

    def remove_stop_words(message):
        return " ".join([word for word in message.lower().split() if word not in stop_words])

    temp['cleaned'] = temp['Message'].apply(remove_stop_words)
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    return wc.generate(temp['cleaned'].str.cat(sep=" "))

def most_common_words(selected_user, df):
    with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
        stop_words = f.read().splitlines()

    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]

    temp = df[df['Sender'] != 'group_notification']
    temp = temp[temp['Message'] != '<Media omitted>\n']
    temp = temp[temp['Message'] != '<omitted media>\n']
    temp = temp[temp['Message'] != '<media omitted>\n']
    temp = temp[temp['Message'] != '<this edited>\n']

    words = []
    for msg in temp['Message']:
        for word in msg.lower().split():
            if word not in stop_words:
                words.append(word)

    return pd.DataFrame(Counter(words).most_common(20), columns=['Word', 'Count'])

def monthly_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]
    timeline = df.groupby(['year', 'month_num', 'month']).count()['Message'].reset_index()
    time = timeline['month'].astype(str) + "-" + timeline['year'].astype(str)
    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]
    daily_timeline = df.groupby(['Date']).count()['Message'].reset_index()
    return daily_timeline

def day_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]
    day_timeline= df.groupby(['Weekday']).count()['Message'].reset_index()
    return day_timeline

def month_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]
    month_timeline= df.groupby(['month']).count()['Message'].reset_index()
    return month_timeline


def detect_sentiment(message):
    return TextBlob(message).sentiment.polarity
def avg_sentiment(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]

    df['Sentiment'] = df['Message'].apply(detect_sentiment)
    average_sentiment = df['Sentiment'].mean()
    sent=""
    if average_sentiment>0.02:
        sent+="Positive"
    elif average_sentiment<-0.02:
        sent+="Negative"
    else :
        sent+="Neutral"
    return average_sentiment,sent

def sentiment_with_time(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]
    df['Sentiment'] = df['Message'].apply(detect_sentiment)
    sentiment_with_time = df.groupby(df['month'])['Sentiment'].mean().reset_index()
    sentiment_with_time['Sentiment_Label'] = sentiment_with_time['Sentiment'].apply(classify_sentiment)

    return sentiment_with_time

def classify_sentiment(score):
        if score > 0.02:
            return 'Positive'
        elif score < -0.02:
            return 'Negative'
        else:
            return 'Neutral'

def sentiment_of_group(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['Sender'] == selected_user]

    df['Sentiment'] = df['Message'].apply(detect_sentiment)
    sentiment_of_users= df.groupby('Sender')['Sentiment'].mean().reset_index()
    sentiment_of_users['Sentiment_Label'] = sentiment_of_users['Sentiment'].apply(classify_sentiment)
    return sentiment_of_users






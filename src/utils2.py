import requests
import urllib.parse
import datetime
import time
import pandas as pd

from src import const,utils,sqlite

def parse_date(epoch_seconds:int):
    """
    エポック時間をyyyy-mm-ddに変換
    """
    dt = datetime.datetime.utcfromtimestamp(epoch_seconds)
    formatted_date = dt.strftime('%Y-%m-%d')
    return formatted_date


def get_pagination_url(hashtag:str , last_tweet_id=''):
    """
    ハッシュタグと最後のツイートIDを元にツイートを取得
    """
    hashtag_encode = urllib.parse.quote(hashtag)
    base = 'https://search.yahoo.co.jp/realtime/api/v1/pagination?crumb=mAPCZQAAAADNdZd0dcgpPQgDqP92PnuPEMSk6lxd4YGq8c2mRAgBCM2UUYvzIQxomlV2QJ6ctst25ElZTfbJIAemJT7h8JGy'
    url = f'{base}&p={hashtag_encode}&rkf=3&b=1'
    if last_tweet_id != '':
        return url + f'&oldestTweetId={last_tweet_id}&start='
    else:
        return url

def get_list(url:str , mode:str , hashtag:str):
    """
    URLを元にツイートのリストを取得
    """
    time.sleep(0.5)
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"response status_code -> {response.status_code} {response}")
    records = []
    for tweet in response.json()['timeline']['entry']:
        id = tweet['id']
        url = tweet['url']
        images = []
        if 'media' in tweet:
            for media in tweet['media']:
                if media['type'] == 'image':
                    image_url = media['item']['mediaUrl']
                    images.append(image_url)
        date = parse_date(tweet['createdAt'])
        user_id = tweet['screenName']
        user_name = tweet['name']
        like_count = tweet['likesCount']

        rec = const.TwitterQueryRecord(
            hashtag,
            mode,
            url,
            date,
            ",".join(images),
            user_id,
            user_name,
            like_count
        )

        if like_count >= 10 and len(images) > 0:
            records.append(rec)
    last_tweet_id = response.json()['timeline']['entry'][-1]['id']
    return records , last_tweet_id

def date_difference(specified_date):
    """
    今日の日付と引数のyyyy-mm-ddを比較して、日数差を返す
    """
    today = datetime.datetime.now().date()
    #specified_date = datetime.datetime.strptime(date_text, "%Y-%m-%d").date()
    difference = abs((today - specified_date).days)
    return difference

def get_tweet(hashtag:str , date:int , mode:str):
    tweets = []
    first_url = get_pagination_url(hashtag)
    records , last_tweet_id = get_list(first_url , mode , hashtag)
    for rec in records:
        tweets.append(
                [
                    rec.url,
                    rec.images,
                    rec.date,
                    rec.userId,
                    rec.userName,
                    rec.likeCount
                ]
            )
    
    index = 0
    while(True):
        url = get_pagination_url(hashtag , last_tweet_id)
        records , last_tweet_id = get_list(url , last_tweet_id , hashtag)
        for rec in records:
            tweets.append(
                [
                    rec.url,
                    rec.images,
                    rec.date,
                    rec.userId,
                    rec.userName,
                    rec.likeCount
                ]
            )
    
        if len(records) > 0:
            last_date = records[-1].date
        if date_difference(last_date) > date:
            break
        print(f"\r　date_range -> {date_difference(last_date)}/{date} | tweets -> {len(tweets)}",end="")
    tweet_df = pd.DataFrame(
        tweets, columns=["url", "images", "date", "userId", "userName", "likeCount"]
    )
    return tweet_df
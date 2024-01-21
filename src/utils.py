#Import-------------------------------------------------------------------------------
from io import StringIO, BytesIO
import os
import re
from time import sleep
import random
from urllib import request
import requests
import chromedriver_autoinstaller
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service
import datetime
import pandas as pd
import platform
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import urllib
from urllib.parse import quote
#--------------------------------------------------------------------------------------
def message(text: str):
    try:
        # 取得したTokenを代入
        line_notify_token = "bLg2L6w7MhUXm5eG1Pyz6jB5IJ8PVU3anYX5FbjUbSc"

        # 送信したいメッセージ
        message = text

        # Line Notifyを使った、送信部分
        line_notify_api = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": f"Bearer {line_notify_token}"}
        data = {"message": f"{message}"}
        requests.post(line_notify_api, headers=headers, data=data)
    except:
        pass

def get_driver(headless=True):
    options = ChromeOptions()
    if headless is True:
        print("Scraping on headless mode.")
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")  # An error will occur without this line
        #user_agent = '"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"'
        #options.add_argument(f'user-agent={user_agent}')
    else:
        options.headless = False
        #user_agent = '"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"'
        #options.add_argument(f'user-agent={user_agent}')
    try:
        driver_path = chromedriver_autoinstaller.install()
        service = Service(executable_path=driver_path)
        # サービスを起動
        driver = webdriver.Chrome(options=options,service=service)
    except Exception as e:
        print('err -> ',e)
        options.binary_location = '/usr/bin/chromium-browser'
        driver = webdriver.Chrome(options=options)
    return driver

def get_url(query:str)-> str:
    parsed = quote(query)
    url = f'https://search.yahoo.co.jp/realtime/search?p={parsed}&ei=UTF-8&mtype=image'
    return url

def date_parse(input_string:str):
    # 現在の日時を取得
    current_time = datetime.datetime.now()

    if ("秒前" in input_string) and ("昨日" not in input_string):
        # "分前" を抽出して分数に変換
        second_ago = int(input_string.split("秒前")[0])
        # 指定された分数だけ過去の日時を計算
        new_time = current_time - datetime.timedelta(seconds=second_ago)

    elif ("分前" in input_string) and ("昨日" not in input_string):
        # "分前" を抽出して分数に変換
        minutes_ago = int(input_string.split("分前")[0])
        # 指定された分数だけ過去の日時を計算
        new_time = current_time - datetime.timedelta(minutes=minutes_ago)
        
    elif "昨日" in input_string:
        output_string = input_string.replace('昨日 ','')
        #　昨日の日時を設定
        time_parts = output_string.split(":")
        new_time = current_time.replace(hour=int(time_parts[0]), minute=int(time_parts[1]), second=0)
        #new_time = new_time + datetime.timedelta(days=-1)

    elif (":" in input_string) and ('月' not in input_string):
        # "16:15" のような場合、今日の日付に指定時刻を設定
        time_parts = input_string.split(":")
        new_time = current_time.replace(hour=int(time_parts[0]), minute=int(time_parts[1]), second=0)
        
    elif (":" not in input_string) and ('月' in input_string) and ('年' in input_string):
        new_time = datetime.datetime.strptime(input_string, "%Y年%m月%d日")
                                              
    else:
        # "9月9日(土) 22:28" のような場合、指定されたフォーマットで日時を解析 9月9日(土) 22:28
        output_string = re.sub(r'\([^)]*\)', '', input_string)
        new_time = datetime.datetime.strptime(output_string, "%m月%d日 %H:%M")
        if new_time.month > current_time.month:
            new_time = new_time.replace(year=current_time.year - 1)
        else:
            new_time = new_time.replace(year=current_time.year)
    return new_time

def get_tweet(query:str,limit:int,date:int,driver):
    print(f'url -> {get_url(query)}')
    driver.get(get_url(query))
    # 現在の日時を取得
    now = datetime.datetime.now()
    date_time = datetime.datetime.now()
    tweets = []
    load_flag = 3
    load_now = 0
    while(True):

        #ツイートのリストを取得
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tweet_links = soup.find_all('div', class_='Tweet_bodyContainer__n_Cs6')

        #ツイートから各要素を取得
        for tweet in tweet_links:
            url = ''
            try:
                url = [link for link in tweet.find_all('a') if 'pic.twitter.com' in link.text][0].text#ツイートリンク
            except:
                url = ''
            try:
                images = [i['src'] for i in [link for link in tweet.find('div','Tweet_imageContainerWrapper__wPE0R').find_all('img') if 'https://rts-pctr.c.yimg.jp' in link['src']]]#画像のリスト
            except:
                images = []

            like_count = 0#いいねっ
            try:
                like_count = int([a for a in tweet.find_all('a') if 'like' in a.get('href','')][0].find('span').text.replace(',',''))
            except:
                like_count = 0
            user_name = tweet.find('a','Tweet_authorID__B1U8c').text#ユーザーID
            display_name = tweet.find('span','Tweet_authorName__V3waK').text#ユーザー名
            
            date_text = tweet.find('time').text
            date_time = date_parse(date_text)

            """
            ・いいね >= 10
            ・画像のあるツイート
            ・未追加のツイート
            ・ツイートリンクのあるツイート
            """
            if like_count >= 10 and len(images) > 0 and len([t for t in tweets if url == t[0]]) == 0 and url != '':
                tweets.append([
                    url,
                    images,
                    date_time,
                    user_name,
                    display_name,
                    like_count
                ])
        print(f'tweet count -> {len(tweets)}')
        if (now - date_time).days > date:
            print('datetime',date_time)
            print(f'date over => {(now - date_time).days}/{date}')
            break

        if len(tweets) > limit:
            print(f'tweet count -> {len(tweets)}')
            print(f'limit over -> limit:{limit}')
            break

        #一番下までスクロール
        for ind in range(8):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(0.25)
        sleep(3)
        try:
            load_btn = driver.find_element(By.LINK_TEXT,"もっと見る")
            load_btn.click()
        except:
            load_now = load_now + 1
            
        if load_now >= load_flag:
            print(f'button over => {load_now} / {load_flag}')
            break
    # breakしたら、データフレームにして保存する
    print(f'{query} result : {len(tweets)}')
    message(f'{query} result : {len(tweets)}')
    tweet_df = pd.DataFrame(
        tweets, columns=["url", "images", "date", "userId", "userName", "likeCount"]
    )
    return tweet_df
import os
import pandas as pd
import yaml
import json

# プロジェクトの相対パス
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# hololive fanart tag list
def holoList():
    holo_path = os.path.join(base_path, "options", "HoloFanArt.csv")
    df = pd.read_csv(holo_path)
    records = []
    for index, row in df.iterrows():
        hashtag = row["hashtag"]
        url = row["url"]
        rec = HoloName(hashtag,url)
        records.append(rec)
    return records


# 各保存先

def sqlite_db():
    return os.path.join(base_path, "sns.db")

# スケジューラーで取得するハッシュタグ
class hashtags:
    def base_hashtags(self):
        csv_path = os.path.join(base_path, "options", "base_sc.csv")
        df = pd.read_csv(csv_path)
        return df["hashtag"].to_list()

    def holo_hashtags(self):
        return holoList()
    
# Option--------------------------------------------------
class options:
    limit_date = 30
    limit_tweets = 3000


def _option_sc() -> dict:
    yaml_path = os.path.join(base_path, "options", "sc_option.yaml")
    with open(yaml_path) as file:
        yml = yaml.safe_load(file)
    return yml


class option_sc:
    def __init__(self):
        self._yml = _option_sc()

    def _get_option(self, key: str):
        date = self._yml[key]["date"]
        limit = self._yml[key]["limit"]
        return date, limit

    def base_option(self):
        return self._get_option("base")

    def holo_option(self):
        return self._get_option("holo")

    def user_option(self):
        return self._get_option("user")

# QueryRecord---------------------------------------------
import datetime

class HoloName:
    def __init__(self,hashtag,url):
        self.hashtag = hashtag
        self.url = url

    def __dict__(self):
        return {"hashtag":self.hashtag,"url":self.url}


class TwitterQueryRecord:
    hashtag: str
    mode: str
    url: str
    date: datetime.date
    images: list[str]
    userId: str
    userName: str
    likeCount: int

    def __init__(
        self,
        hashtag: str,
        mode: str,
        url: str,
        date: str,
        images: str,
        userId: str,
        userName: str,
        likeCount: int,
    ):
        self.hashtag = hashtag
        self.mode = mode
        self.url = url
        self.date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        self.images = images.split(",")
        self.userId = userId
        self.userName = userName
        self.likeCount = likeCount

    def __str__(self):
        return (
            f"Hashtag: {self.hashtag}\n"
            f"Mode: {self.mode}\n"
            f"URL: {self.url}\n"
            f"Date: {self.date}\n"
            f"Images: {self.images}\n"
            f"User ID: {self.userId}\n"
            f"User Name: {self.userName}\n"
            f"Like Count: {self.likeCount}\n"
        )

    def __dict__(self):
        return {
            "hashtag": self.hashtag,
            "mode": self.mode,
            "url": self.url,
            "date": self.date.strftime("%Y-%m-%d"),
            "images": self.images,
            "userId": self.userId,
            "userName": self.userName,
            "likeCount": self.likeCount,
        }

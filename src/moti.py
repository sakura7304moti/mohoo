from . import const,utils2,sqlite
from tqdm import tqdm
holoList = const.holoList()

class Scraper:
    def base_scraper(self, query: str, date: int = 30, limit: int = 3000):
        df = utils2.get_tweet(query,date,'base')
        sqlite.update(df,query,'base')
        
    def holo_scraper(self, date: int = 30, limit: int = 3000):
        for query in tqdm(holoList,desc="holo scraper"):
            hashtag = query.hashtag
            print(f'Fanart : {hashtag}')
            df = utils2.get_tweet(hashtag,date,'holo')
            sqlite.update(df,hashtag,'holo')
        driver.close()
from src import moti,utils,const
import shutil

try:
    utils.message("scheduler start")
    model = moti.Scraper()
    option = const.option_sc()
    tag = const.hashtags()
    """
    BASE
    """
    utils.message('base mode start')
    date, limit = option.base_option()
    hashtags = tag.base_hashtags()
    for p in hashtags:
        print(f'hashtag -> {p}')
        utils.message(f'hashtag : {p}')
        model.base_scraper(p, date, limit)
    utils.message('base mode end')
    """
    HOLO
    """
    utils.message('holo mode start')
    date, limit = option.holo_option()
    model.holo_scraper(date, limit)
    utils.message('holo mode end')
    """
    USER
    """
    utils.message("scheduler end")
    """
    file copy
    """
    shutil.copyfile(const.sqlite_db(),r'Z:\Python\monitter\sns.db')
    shutil.copyfile(const.sqlite_db(),r'Z:\git\sharemotiApi2\scraper\database\twitter.db')
    shutil.copyfile(const.sqlite_db(),r'X:\server\git\sharemotiApi2\scraper\database\twitter.db')
except Exception as e:
    print(e)
    utils.message(e)
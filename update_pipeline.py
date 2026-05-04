import schedule
import time

from crawler_ddg import run_crawler
from deep_scraper import run_scraper



def pipeline():
    run_crawler()
    run_scraper()

    print("Dataset updated")


schedule.every().week.do(pipeline)


while True:
    schedule.run_pending()
    time.sleep(60)
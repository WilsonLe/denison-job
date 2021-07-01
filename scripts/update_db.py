from utils import Redis
from utils import JobScraper
from utils import Emailer
from pprint import pprint
import os
from dotenv import load_dotenv
load_dotenv()


def main():
    """update database with current jobs on web app.
    This is to avoid sending test email when resetting
    redis database
    """
    js = JobScraper()
    r1 = Redis(
        os.getenv('REDIS_HOST_1'),
        os.getenv('REDIS_PORT_1'),
        os.getenv('REDIS_PASS_1'),
        db=0)
    js.start()
    if not js.logged_in():
        js.login()

    current_jobs = js.get_current_jobs()
    for job in current_jobs:
        r1.set_key(job['uid'], job)

    pprint(r1.get_db())
    js.stop()


main()

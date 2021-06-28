from utils import Redis
from utils import JobScraper
import os
from dotenv import load_dotenv
load_dotenv()


def main():
    js = JobScraper()
    r = Redis(
        os.getenv('REDIS_HOST'),
        os.getenv('REDIS_PORT'),
        os.getenv('REDIS_PASS'))
    js.start()

    if not js.logged_in():
        js.login()

    current_jobs = js.get_current_jobs()
    current_jobs_id = list(map(lambda job: job['uid'], current_jobs))

    previous_jobs = list(map(lambda key: r.get_db()[key], r.get_db().keys()))
    previous_jobs_id = list(map(lambda job: job['uid'], previous_jobs))

    added_jobs_id = list(set(current_jobs_id) - set(previous_jobs_id))
    added_jobs = list(filter(
        lambda job: job['uid'] in added_jobs_id, added_jobs_id))

    removed_jobs_id = list(set(previous_jobs_id) - set(current_jobs_id))
    removed_jobs = list(filter(
        lambda job: job['uid'] in added_jobs_id, removed_jobs_id))

    print(f'added jobs: {added_jobs}')
    print(f'removed jobs: {removed_jobs}')

    if len(added_jobs) == 0 and len(removed_jobs) != 0:

        # remove keys from db
        for removed_job in removed_jobs:
            r.del_key(removed_job['uid'])

        # send email to notify of removed jobs
        pass
    elif len(added_jobs) != 0 and len(removed_jobs) == 0:

        # add keys to db
        for added_job in added_jobs:
            r.set_key(added_job['uid'], added_job)

        # send email to notify of added jobs
        pass
    elif len(added_jobs) != 0 and len(removed_jobs) != 0:

        # add and remove keys from db
        for added_job in added_jobs:
            r.set_key(added_job['uid'], added_job)
        for removed_job in removed_jobs:
            r.del_key(removed_job['uid'])

        # send email to notify of added and removed jobs
        pass

    js.stop()


main()

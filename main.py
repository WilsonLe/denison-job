from flask import Flask, request, redirect, url_for
from selenium.common.exceptions import NoSuchWindowException
from utils import Emailer, JobScraper, Redis
from datetime import datetime
import secrets
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from time import sleep
import threading as thr
import multiprocessing as mp
mp.set_start_method("fork")
load_dotenv()


def run_app(js, e, r1, r2):
    if not js.logged_in():
        url_token = secrets.token_urlsafe(32)
        notify_admin(url_token, e)
        admin_accept = mp.Event()
        p = mp.Process(target=start_admin_listener,
                       args=(url_token, admin_accept, js, e))

        p.start()
        admin_accept.wait()
        print("admin accepted")
        sys.stdout.flush()
        p.terminate()
        p.join()

    print('exit login check')
    sys.stdout.flush()
    current_jobs = js.get_current_jobs()
    current_jobs_id = list(map(lambda job: job['uid'], current_jobs))

    previous_jobs = list(map(lambda key: r1.get_db()[key], r1.get_db().keys()))
    previous_jobs_id = list(map(lambda job: job['uid'], previous_jobs))

    added_jobs_id = list(set(current_jobs_id) - set(previous_jobs_id))
    added_jobs = list(filter(
        lambda job: job['uid'] in added_jobs_id, current_jobs))

    removed_jobs_id = list(set(previous_jobs_id) - set(current_jobs_id))
    removed_jobs = list(filter(
        lambda job: job['uid'] in removed_jobs_id, previous_jobs))

    print(datetime.now())
    print(f'number of added jobs: {len(added_jobs)}')
    print(f'number of removed jobs: {len(removed_jobs)}')
    sys.stdout.flush()

    if len(added_jobs) == 0 and len(removed_jobs) != 0:

        # remove keys from db
        for removed_job in removed_jobs:
            r1.del_key(str(removed_job['uid']))

        # send email to notify of removed jobs
        html_message = """
        <h1>Some student jobs have been removed!</h1>
        """
        for job in removed_jobs:
            html_message += f"""
                <a href=\"{job['href']}\">
                    <h3>{job['title']}, {job['department']}</h3>
                </a>
            """

        for address in r2.get_all_keys():
            e.send(address, 'Denison Student Jobs Updates', html_message)
        print('Notified users')
        sys.stdout.flush()
    elif len(added_jobs) != 0 and len(removed_jobs) == 0:

        # add keys to db
        for added_job in added_jobs:
            r1.set_key(added_job['uid'], added_job)

        # send email to notify of added jobs
        html_message = """
        <h1>Some student jobs have been added!</h1>
        """
        for job in added_jobs:
            html_message += f"""
                <a href=\"{job['href']}\">
                    <h3>{job['title']}, {job['department']}</h3>
                </a>
            """

        for address in r2.get_all_keys():
            e.send(address, 'Denison Student Jobs Updates', html_message)
        print('Notified users')
        sys.stdout.flush()
    elif len(added_jobs) != 0 and len(removed_jobs) != 0:

        # add and remove keys from db
        for added_job in added_jobs:
            r1.set_key(added_job['uid'], added_job)
        for removed_job in removed_jobs:
            r1.del_key(str(removed_job['uid']))

        # send email to notify of added and removed jobs
        html_message = """
        <h1>Some student jobs have been added and removed!</h1>
        """

        html_message += """
            <h2>Added jobs: </h2>
        """
        for job in added_jobs:
            html_message += f"""
                <a href=\"{job['href']}\">
                    <h3>{job['title']}, {job['department']}</h3>
                </a>
            """

        html_message += """
            <h2>Removed jobs: </h2>
        """
        for job in removed_jobs:
            html_message += f"""
                <a href=\"{job['href']}\">
                    <h3>{job['title']}, {job['department']}</h3>
                </a>
            """
        for address in r2.get_all_keys():
            e.send(address, 'Denison Student Jobs Updates', html_message)
        print('Notified users')
        sys.stdout.flush()
    sleep(int(os.getenv('INTERVAL')))


def notify_admin(url_token, e):
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    url = f'{HOST}:{PORT}/{url_token}'
    e.send(os.getenv('ADMIN_MAIL'),
           'Denison Jobs Application Requires Login', url)
    print("Email sent")
    sys.stdout.flush()


def start_admin_listener(url_token, admin_accept, js, e):
    app = Flask(__name__)

    @app.route(f"/{url_token}")
    def login_then_shutdown():
        try:
            js.login()
            sys.stdout.flush()
            thr.Timer(2.0, lambda: admin_accept.set()).start()
            return "DONE"
        except Exception as ex:
            with open('exceptions.txt', 'w') as f:
                f.write(str(datetime.now()))
                f.write(ex)
            e.send(os.getenv('ADMIN_MAIL'),
                   'Denison Job Exception Occured', str(ex))
            raise ex
    app.run('0.0.0.0', os.getenv('PORT'))


def main():

    js = JobScraper()
    r1 = Redis(
        os.getenv('REDIS_URL_1'),
        os.getenv('REDIS_HOST_1'),
        os.getenv('REDIS_PORT_1'),
        os.getenv('REDIS_PASS_1'))
    r2 = Redis(
        os.getenv('REDIS_URL_2'),
        os.getenv('REDIS_HOST_2'),
        os.getenv('REDIS_PORT_2'),
        os.getenv('REDIS_PASS_2'))
    e = Emailer(
        os.getenv('MAIL_ADDRESS'),
        os.getenv('MAIL_PASS'))
    js.start()
    while True:
        run_app(js, e, r1, r2)

    js.stop()
    print('APPLICATION STOPPED')


if __name__ == "__main__":
    main()

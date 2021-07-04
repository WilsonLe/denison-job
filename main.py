from flask import Flask, request, redirect, url_for
import socket
from utils import Emailer, JobScraper, Redis

import secrets
import os
from datetime import datetime
from dotenv import load_dotenv
from time import sleep
import multiprocessing as mp
mp.set_start_method("fork")
load_dotenv()


def run_app(js, e, r1, r2):
    if not js.logged_in():
        url_token = secrets.token_urlsafe(32)
        notify_admin(url_token, e)
        p = mp.Process(target=start_admin_listener, args=(url_token, js))
        p.start()
        # TODO: write external script to get system 0.0.0.0 ip address, then parse into url to send in email
        p.join()
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

    if len(added_jobs) == 0 and len(removed_jobs) != 0:

        # remove keys from db
        for removed_job in removed_jobs:
            r1.del_key(removed_job['uid'])

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

    elif len(added_jobs) != 0 and len(removed_jobs) != 0:

        # add and remove keys from db
        for added_job in added_jobs:
            r1.set_key(added_job['uid'], added_job)
        for removed_job in removed_jobs:
            r1.del_key(removed_job['uid'])

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

    sleep(int(os.getenv('INTERVAL')))


def notify_admin(url_token, e):
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    url = f'{HOST}:{PORT}/{url_token}'
    e.send(os.getenv('ADMIN_MAIL'),
           'Denison Jobs Application Requires Login', url)


def start_admin_listener(url_token, js):
    app = Flask(__name__)

    @app.route("/ip")
    def host_ip():
        print(request.url_root)
        return "HI"

    @app.route(f"/{url_token}")
    def login_then_shutdown():
        try:
            js.login()
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()
            return "DONE"
        except Exception as e:
            return e

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


if __name__ == "__main__":
    main()

from utils import JobScraper


def main():
    js = JobScraper()
    js.start()

    if not js.logged_in():
        js.login()

    jobs = js.get_current_jobs()
    print(jobs)
    js.stop()


main()

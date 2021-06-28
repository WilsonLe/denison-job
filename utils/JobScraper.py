import os
import re
import redis

from dotenv import load_dotenv

from .WebDriver import WebDriver
load_dotenv()


class JobScraper(WebDriver):
    def __init__(self):
        self.JOB_URL = 'https://webapps.denison.edu/stuemp/search.php'
        self.INTERVAL = 5  # Every 5 seconds
        WebDriver.__init__(self)

    def login(self):
        """Login to my denison. Assume driver has already started.
        """
        self.go_to('my.denison.edu')
        self.query_selector('#username').send_keys(os.getenv('US'))
        self.query_selector('#password').send_keys(os.getenv('PW'))
        self.query_selector(
            '#loginForm > div:nth-child(7) > div > button').click()
        self.wait_for_and_switch_to_iframe('duo_iframe')
        self.wait_for('#remember_me_label_text')
        self.query_selector('#remember_me_label_text').click()
        self.wait_for(
            '#auth_methods > fieldset > div.row-label.push-label > button')
        self.query_selector(
            '#auth_methods > fieldset > div.row-label.push-label > button').click()
        self.switch_default()
        self.wait_for('#mydenison-header', timeout=59)
        print('LOGGED IN')

    def logged_in(self):
        """check if current driver has already logged into mydenison

        Returns:
            bool: True if already logged in, else False
        """
        self.go_to('my.denison.edu')
        self.sleep(5)
        element = self.query_selector('#mydenison-header')
        if element != None:
            return True
        else:
            return False

    def get_current_jobs(self):
        """fetch current jobs from denison web apps. Assumed that user has
        already logged in

        Returns:
            list: jobs currently avaiable on my denison web app
        """
        # Get jobs elements
        self.go_to(self.JOB_URL)
        lightRows = self.query_selector('.light-row')
        darkRows = self.query_selector('.dark-row')
        allRows = lightRows + darkRows
        allRows = list(
            map(lambda row: row.find_elements_by_tag_name('td'), allRows))

        # Extracting job general info
        fetched_jobs = []
        for row in allRows:
            href = row[0].find_element_by_tag_name('a').get_attribute('href')
            title = row[0].find_element_by_tag_name('a').text
            department = row[1].text
            job_id = re.search('job_id=[0-9]+', href).group(0)
            uid = re.search('[0-9]+', job_id).group(0)
            fetched_jobs.append({
                "title": title,
                "href": href,
                "department": department,
                "uid": uid
            })

        return fetched_jobs

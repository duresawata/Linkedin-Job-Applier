from gettext import find
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import time
import re
import csv
from datetime import datetime
import os

class ApplyLinkedin:
    def __init__(self, email, phone, username, password, driverPath, jobTitle, state, resumeLocation, num_loops, follow_company=None, city=None):
        # "parameter Initialization"
        self.username = username
        self.email = email
        self.password = password
        self.keywords = jobTitle
        self.city = city
        self.state = state
        self.location = city
        self.phone = phone
        self.resume = resumeLocation
        self.driver = webdriver.Chrome(driverPath)
        self.num_loops = num_loops
        self.applied_jobs = []

    def login_linkedin(self):
        self.driver.maximize_window()
        self.driver.get("https://www.linkedin.com/login")
        login_email = self.driver.find_element_by_name('session_key')
        login_email.clear()
        login_email.send_keys(self.email)

        time.sleep(1)

        login_password = self.driver.find_element_by_name('session_password')
        login_password.clear()
        login_password.send_keys(self.password)
        login_password.send_keys(Keys.RETURN)
    
    def job_search(self):
        job_link = self.driver.find_element_by_link_text('Jobs')
        job_link.click()

        time.sleep(1)

        search_keyword = self.driver.find_element_by_xpath("//input[starts-with(@id,'jobs-search-box-keyword')]")
        search_keyword.clear()
        search_keyword.send_keys(self.keywords)
        time.sleep(1)
        search_location = self.driver.find_element_by_xpath("//input[starts-with(@id,'jobs-search-box-location')]")
        search_location.clear()
        search_location.send_keys(self.location)
        search_link = self.driver.find_element_by_class_name('jobs-search-box__submit-button')
        search_link.click()
        time.sleep(3)
    
    def filter(self):
        # filter by easy apply
        easy_apply_button = self.driver.find_element_by_xpath("/html/body/div[6]/div[3]/div[3]/section/div/div/div/ul/li[8]/div/button")
        easy_apply_button.click()
        time.sleep(2)

    def find_offers(self):
        total_results = self.driver.find_element_by_class_name("display-flex.t-12.t-black--light.t-normal")
        total_results_int = int(total_results.text.split(' ',1)[0].replace(",",""))
        print(total_results_int)

        time.sleep(2)
        current_page = self.driver.current_url
        results = self.driver.find_elements_by_class_name("jobs-search-results__list-item.occludable-update.p0.relative.ember-view")

        for result in results:
            hover = ActionChains(self.driver).move_to_element(result)
            hover.perform()
            titles = self.driver.find_elements_by_class_name("disabled.ember-view.job-card-container__link.job-card-list__title")
            for title in titles:
                self.submit_application(title)
            
        # if there is more than just one page, find all page and submit for all page results
        if total_results_int > 24:
            time.sleep(2)

            # find the last page and construct url of each page based on the total amount of pages
            find_pages = self.driver.find_element_by_class_name("artdeco-pagination__indicator.artdeco-pagination__indicator--number")
            total_pages = find_pages[len(find_pages)-1].text
            total_pages_int = int(re.sub(r"[^\d.]", "", total_pages))
            
            get_last_page = self.driver.find_element_by_xpath("//button[@aria-label='Page "+str(total_pages_int)+"']")
            get_last_page.send_keys(Keys.RETURN)
            time.sleep(2)
            last_page = self.driver.current_url
            total_jobs = int(last_page.split('start=',1)[1])

            # go through all available pages and job offers and apply
            for page_number in range(25,total_jobs+25,25):
                self.driver.get(current_page+'&start='+str(page_number))
                time.sleep(2)
                results_ext = self.driver.find_elements_by_class_name("jobs-search-results__list-item.occludable-update.p0.relative.ember-view")
                for result_ext in results_ext:
                    hover_ext = ActionChains(self.driver).move_to_element(result_ext)
                    hover_ext.perform()
                    titles_ext = result_ext.find_elements_by_class_name('disabled.ember-view.job-card-container__link.job-card-list__title')
                    for title_ext in titles_ext:
                        self.submit_application(title_ext)
        else:
            self.close_session()

    def saveJobs_submitted(self, name):
        headers = ["Job_Name", "Applied_Date"]

        now = datetime.now()
        start_date = now.strftime("%y/%m/%y")
        myDict = {"Job_Name": name, "Applied_Date": start_date}
        filename = "AppliedJobs.csv"

        if os.path.isfile(filename):
            with open(filename, "a", newline="") as my_file:
                w = csv.DictWriter(my_file, fieldnames=headers)
                w.writerow(myDict)
        else:
            with open(filename, "w", newline="") as my_file:
                w = csv.DictWriter(my_file, fieldnames=headers)
                w.writeheader()
                w.writerow(myDict)

    def submit_application(self, job_ad):
        print("You are applying for: ", job_ad.text)
        job_ad.click()
        time.sleep(2)

        # click the easy appy button, skip if already applied to the position

        try:
            in_apply = self.driver.find_element_by_xpath("/html/body/div[6]/div[3]/div[3]/div[2]/div/section[2]/div/div/div[1]/div/div[1]/div/div[2]/div[3]/div/div/div/button")
            in_apply.click()
        except NoSuchElementException:
            print("You are already applied to this job, go to next job ...")
            pass
        time.sleep(2)

        # try to fill and  submit application if the application is available
        try:
            phone_area = self.driver.find_element_by_xpath("//*[@id='urn:li:fs_easyApplyFormElement:(urn:li:fs_normalized_jobPosting:2884199530,9,phoneNumber~nationalNumber)']")
            phone_area.clear()
            phone_area.send_keys(self.phone)

            time.sleep(3)

            upload_resume = self.driver.find_element_by_class_name("jobs-document-upload__upload-button")
            upload_resume.clear()
            upload_resume.send_keys(self.resume)

            time.sleep(3)
            
            submit = self.driver.find_element_by_xpath("/html/body/div[3]/div/div/div[2]/div/form/footer/div[3]/button/span")
            submit.click()
            self.applied_jobs.append(job_ad.text)
            # save applied jobs to spreadsheet
            self.saveJobs_submitted(job_ad.text)
            print("*************successfully appled to " + job_ad.text+ ". Congratulations*********")
            time.sleep(3)

            # exit after submit

            submit_back = self.driver.find_element_by_xpath("/html/body/div[3]/div/div/button")
            submit_back.click()
            time.sleep(3)

            # if it is not available the button, discard the application and go to next
        except NoSuchElementException:
            print("not direct application. going to next ...")

            #incase we dont have discard button
            try:
                discard = self.driver.find_element_by_xpath("/html/body/div[3]/div/div/button")
                discard.send_keys(Keys.RETURN)
                time.sleep(2)
                discard_confirm = self.driver.find_element_by_xpath("/html/body/div[3]/div[2]/div/div[3]/button[2]")
                discard_confirm.send_keys(Keys.RETURN)
                time.sleep(1)
            except NoSuchElementException:
                pass
        time.sleep(1)
    def close_session(self):
        """This function closes the actual session"""
        print('End of the session, see you later!')
        self.driver.close()
    
    def init_driver(self):
        """Initializes instance of webdriver"""
        return self.driver

    
    
    
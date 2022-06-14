from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import os
import glob
import time
from uuid import uuid4


class Pubmed:

    def __init__(self, url: str):
        os.environ["GH_TOKEN"] = "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"

        self.uid = uuid4().hex
        self.directory = f"{os.path.abspath(os.curdir)}/data/{self.uid}"

        self.url = url
        self.total_pages = None
        self.actual_page = 1

        self.service = Service(executable_path=ChromeDriverManager().install())
        self.options = Options()
        prefs = {"download.default_directory": self.directory}
        self.options.add_experimental_option("prefs", prefs)

    def RetrieveArticles(self):

        driver = webdriver.Chrome(service=self.service, chrome_options=self.options)
        driver.implicitly_wait(1)

        driver.get(self.url)

        if not self.total_pages:
            total_pages = driver.find_element(by=By.CLASS_NAME, value="of-total-pages")
            self.total_pages = int(total_pages.text.split(" ")[1].strip())
            print(self.total_pages, type(self.total_pages))

        while self.actual_page <= self.total_pages:
            self._RetrieveArticle(driver)

        time.sleep(10)
        driver.quit()

    def _RetrieveArticle(self, _driver):

        button = _driver.find_element(by=By.ID, value='save-results-panel-trigger')
        button.click()

        select = Select(_driver.find_element(by=By.ID, value='save-action-selection'))
        select.select_by_visible_text('All results on this page')

        select = Select(_driver.find_element(by=By.ID, value='save-action-format'))
        select.select_by_visible_text('PubMed')

        button2 = _driver.find_element(by=By.CLASS_NAME, value='action-panel-submit')
        _driver.execute_script("arguments[0].click();", button2)

        self.url = self.url.replace(f"page={self.actual_page}", f"page={self.actual_page + 1}")
        self.actual_page += 1

    def UnifyFiles(self):

        dictionary = {"AB": "", "AD": "", "AID": "", "DP": "", "FAU": "", "IR": "", "JT": "", "MH": "", "OT": "",
                      "PL": "", "PMID": "", "PT": "", "RN": "", "TI": ""}

        for file in glob.glob(f"{self.directory}/*.txt"):
            file = open(file, "r").read()
            print(file)

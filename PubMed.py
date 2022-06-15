from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementClickInterceptedException
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import os
import platform
import glob
import time
from uuid import uuid4
import pandas as pd

class Pubmed:

    all_tag = ["PMID", "OWN", "STAT", "DCOM", "LR", "IS", "VI", "DP", "TI", "PG", "LID", "AB", "CI", "FAU",
               "AU", "AD", "LA", "PT", "DEP", "PL", "TA", "JT", "JID", "SB", "MH", "OTO", " OT", "EDAT", "MHDA",
               "CRDT", "PHST", "AID", "PST", "SO"]

    valid_tag = ["AB", "AD", "AID", "DP", "FAU", "IR", "JT", "MH", "OT", "PL", "PMID", "PT", "RN", "TI"]

    def __init__(self, keyword: str):
        os.environ["GH_TOKEN"] = "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"

        self.uid = uuid4().hex
        self.directory = f"{os.path.abspath(os.curdir)}/data/temp/{self.uid}"
        self.directory = self.directory if platform.system() == "Linux" else self.directory.replace("/", "\\")

        self.url = f"https://pubmed.ncbi.nlm.nih.gov/?term={keyword}&filter=hum_ani.humans&filter=years.2000-2022&size=200&page=1"
        self.final_dataframe = None

        self.service = Service(executable_path=ChromeDriverManager().install())
        self.options = Options()
        self.options.add_argument("--disable-notifications")
        prefs = {"download.default_directory": self.directory}
        self.options.add_experimental_option("prefs", prefs)

    def RetrieveArticles(self):
        driver = webdriver.Chrome(service=self.service, options=self.options)
        driver.implicitly_wait(0.2)

        driver.get(self.url)

        while True:
            try:
                self._SeleniumActions(driver)
            except ElementClickInterceptedException:
                break

        driver.quit()

        self.final_dataframe = self._UnifyFiles()
        self.final_dataframe.to_csv("final_csv.csv")

    @staticmethod
    def _SeleniumActions(_driver):

        open_save_window = _driver.find_element(by=By.ID, value='save-results-panel-trigger')
        open_save_window.click()

        select_result = Select(_driver.find_element(by=By.ID, value='save-action-selection'))
        select_result.select_by_visible_text('All results on this page')

        select_format = Select(_driver.find_element(by=By.ID, value='save-action-format'))
        select_format.select_by_visible_text('PubMed')

        save_button = _driver.find_element(by=By.CLASS_NAME, value='action-panel-submit')
        _driver.execute_script("arguments[0].click();", save_button)

        next_page = _driver.find_element(by=By.XPATH, value="//div[@class='top-pagination']//button[@class='button-wrapper next-page-btn']")
        next_page.click()

    def _UnifyFiles(self):

        dataframe_list = self._TransformTxtToDataframe()

        final_df = None
        for df in dataframe_list:
            print("actual df:", df.shape)
            if final_df is None:
                final_df = df
            else:
                final_df = pd.concat([final_df, df])

        print(final_df.shape)
        return final_df.reset_index(drop=True)

    def _TransformTxtToDataframe(self):

        object_files = glob.glob(f"{self.directory}/*.txt") if platform.system() == "Linux" else glob.glob(f"{self.directory}\\*.txt")
        dataframe_list = []

        for file in object_files:
            file = open(file, "r", encoding='utf-8').read()

            self.dictionary = {"AB": [], "AD": [], "AID": [], "DP": [], "FAU": [], "IR": [], "JT": [], "MH": [], "OT": [],
                          "PL": [], "PMID": [], "PT": [], "RN": [], "TI": []}

            articles = file.split("\n\n")

            for article in articles:

                article_dictionary = {"AB": "", "AD": "", "AID": "", "DP": "", "FAU": "", "IR": "", "JT": "", "MH": "",
                                      "OT": "",
                                      "PL": "", "PMID": "", "PT": "", "RN": "", "TI": ""}

                article = article.split("\n")

                last_tag = ""
                for tag in article:
                    tag = tag.split("- ")
                    name_tag = tag[0].strip()
                    last_tag = tag[0].strip() if tag[0].strip() in Pubmed.all_tag else last_tag

                    if name_tag not in Pubmed.valid_tag:
                        if name_tag not in Pubmed.all_tag and last_tag in Pubmed.valid_tag:
                            article_dictionary[last_tag] += f" {name_tag}"
                        else:
                            pass
                    else:
                        article_dictionary[name_tag] += tag[1] if len(article_dictionary[name_tag]) < 1 else "$#$" + \
                                                                                                             tag[1]
                        last_tag = name_tag

                for k, v in article_dictionary.items():
                    self.dictionary[k].append(v)

            df = pd.DataFrame(self.dictionary)
            dataframe_list.append(df)

        return dataframe_list

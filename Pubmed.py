from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementClickInterceptedException
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import os
import shutil
import platform
import glob
import time
from uuid import uuid4
import pandas as pd
from datetime import datetime
import re

class Pubmed:

    all_tag = ["PMID", "OWN", "STAT", "DCOM", "LR", "IS", "VI", "DP", "TI", "PG", "LID", "AB", "CI", "FAU",
               "AU", "AD", "LA", "PT", "DEP", "PL", "TA", "JT", "JID", "SB", "MH", "OTO", " OT", "EDAT", "MHDA",
               "CRDT", "PHST", "AID", "PST", "SO"]

    valid_tag = ["AB", "AD", "AID", "DP", "FAU", "IR", "JT", "MH", "OT", "PL", "PMID", "PT", "RN", "TI"]

    tag_translation = {"AB": "Abstract", "AD": "Affiliation", "AID": "Article_identifier",
                       "DP": "Publication_date", "FAU": "Full_author_name", "IR": "Investigator",
                       "JT": "Full_journal", "MH": "Mesh_terms", "OT": "Other_term",
                       "PL": "Place_of_publication", "PMID": "PMID", "PT": "Publication_type",
                       "RN": "EC_RN_number", "TI": "Title"}

    def __init__(self, keyword: str):
        os.environ["GH_TOKEN"] = "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"

        self.uid = uuid4().hex
        self.directory = f"{os.path.abspath(os.curdir)}/data/temp/{self.uid}"
        self.directory = self.directory if platform.system() == "Linux" else self.directory.replace("/", "\\")

        self.pathologie = keyword
        self.url = f"https://pubmed.ncbi.nlm.nih.gov/?term={self.MeshTermsSelection(keyword)}&filter=hum_ani.humans&filter=dates.2000%2F1%2F1-{datetime.now().year}%2F12%2F31&size=200"
        self.final_dataframe = None

        self.service = Service(executable_path=ChromeDriverManager().install())
        self.options = Options()
        self.options.add_argument("--disable-notifications")
        prefs = {"download.default_directory": self.directory}
        self.options.add_experimental_option("prefs", prefs)

    @staticmethod
    def MeshTermsSelection(pathologie: str):
        pathologie = pathologie.lower().strip()

        if pathologie == "hyperthyroidie":
            return "((((((((((hyperthyroidism[MeSH Terms]) OR (hyperthyroidism[Text Word])) OR (hyperthyroid[Text Word])) OR (graves disease[MeSH Terms])) OR (graves disease[Text Word])) OR (basedow[Text Word])) OR (thyrotoxicosis[MeSH Terms])) OR (thyrotoxicosis[Text Word])) OR (thyroid crisis[Text Word])) OR (crisis thyroid[Text Word])) OR (thyroid crisis[MeSH Terms])"
        elif pathologie == "hypothyroidie":
            return "(((((((((((hypothyroidism[MeSH Terms]) OR (hypothyroidism[Text Word])) OR (congenital hypothyroidism[MeSH Terms])) OR (cretinism[Text Word])) OR (congenital iodine deficiency syndrome[Text Word])) OR (lingual thyroid[MeSH Terms])) OR (thyroid dysgenesis[Text Word])) OR (lingual thyroid[Text Word])) OR (thyroid lingual[Text Word])) OR (lingual goiter[MeSH Terms])) OR (lingual goiter[Text Word])) OR (goiter lingual[Text Word])"
        elif pathologie == "goitre":
            return "((goiter[MeSH Terms]) OR (goiter[Text Word]) OR (goiters[Text Word])) OR ((goiter, nodular[MeSH Terms]) OR (nodular goiters[Text Word]) OR (nodular goiter[Text Word]) OR (goiter, nodular[Text Word]))"
        elif pathologie == "thyroidites":
            return "(((((((((((thyroiditis, autoimmune[MeSH Terms]) OR (thyroiditis[Text Word])) OR (hashimoto disease[MeSH Terms])) OR (hashimoto[Text Word]))) OR (postpartum thyroiditis[MeSH Terms])) OR (postpartum thyroiditis[Text Word])) OR (thyroiditis, subacute[MeSH Terms])) OR (thyroiditis, subacute[Text Word])) OR (subacute thyroiditis[Text Word])) OR (subacute thyroiditis[Text Word])) OR (thyroiditis, suppurative[MeSH Terms])"
        else:
            raise ValueError

    def RetrieveArticles(self):
        driver = webdriver.Chrome(service=self.service, options=self.options)
        driver.implicitly_wait(0.2)

        driver.get(self.url)
        total_results = int(driver.find_element(by=By.CLASS_NAME, value="value").text.replace(",", ""))
        year_range = [2000, 2001]

        while year_range[1] <= datetime.now().year+2:

            driver.get(re.sub(r"dates.\d{4}%2F1%2F1-\d{4}", f"dates.{year_range[0]}%2F1%2F1-{year_range[1]}", self.url))
            self._SeleniumActions(driver)

            year_range = [x+2 for x in year_range]

        time.sleep(10)
        driver.quit()

        self.final_dataframe = self._UnifyFiles()

        shutil.rmtree(self.directory)

        if self.final_dataframe.shape[0] < total_results:
            print(f"Missing articles for object with uid: {self.uid}, pathologie: {self.pathologie}, new try.")
            self.RetrieveArticles()

    @staticmethod
    def _SeleniumActions(_driver):

        open_save_window = _driver.find_element(by=By.ID, value='save-results-panel-trigger')
        open_save_window.click()

        select_result = Select(_driver.find_element(by=By.ID, value='save-action-selection'))
        select_result.select_by_visible_text('All results')

        select_format = Select(_driver.find_element(by=By.ID, value='save-action-format'))
        select_format.select_by_visible_text('PubMed')

        save_button = _driver.find_element(by=By.CLASS_NAME, value='action-panel-submit')
        _driver.execute_script("arguments[0].click();", save_button)

        # next_page = _driver.find_element(by=By.XPATH, value="//div[@class='top-pagination']//button[@class='button-wrapper next-page-btn']")
        # next_page.click()

    def _UnifyFiles(self):

        dataframe_list = self._TransformTxtToDataframe()

        final_df = None
        for df in dataframe_list:
            if final_df is None:
                final_df = df
            else:
                final_df = pd.concat([final_df, df])

        final_df = final_df.rename(columns={col: Pubmed.tag_translation[col] for col in final_df.columns}).drop_duplicates().reset_index(drop=True)

        return final_df

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
                        article_dictionary[name_tag] += tag[1] if len(article_dictionary[name_tag]) < 1 else "---" + \
                                                                                                             tag[1]
                        last_tag = name_tag

                for k, v in article_dictionary.items():
                    self.dictionary[k].append(v)

            df = pd.DataFrame(self.dictionary)
            dataframe_list.append(df)

        return dataframe_list

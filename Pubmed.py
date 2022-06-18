from modules import *

class Pubmed:

    # Ajouter les filtres pubmed en argument
    def __init__(self, pathologie: str = None, filters: list = None, delay: float = 1):

        self.__InitializeObjectVariables__(pathologie, delay)
        self.__InitializeURL__(filters)
        self.__InitializeSelenium__()

    def RetrieveArticles(self):
        driver = webdriver.Chrome(service=self.service, options=self.options)
        driver.implicitly_wait(0.5)

        driver.get(self.url)
        print("get")
        total_results = int(driver.find_element(by=By.CLASS_NAME, value="value").text.replace(",", ""))
        articles_files_count = 0
        year_range = [2000, 2001]

        while year_range[1] <= datetime.now().year + 2:

            # Met à jour les dates de l'url
            driver.get(re.sub(r"dates.\d{4}%2F1%2F1-\d{4}", f"dates.{year_range[0]}%2F1%2F1-{year_range[1]}", self.url))

            try:
                self._SeleniumActions(driver)
                year_range = [x + 2 for x in year_range]
                articles_files_count += 1

            except ElementClickInterceptedException as error:
                print(str(error).split("Stacktrace:")[0])
                print(f"Error from {self.uid}, pathologie: {self.pathologie}, new try.\n\n")

                driver.refresh()
            except ElementNotInteractableException as error:
                print(str(error).split("Stacktrace:")[0])
                print(f"Error from {self.uid}, pathologie: {self.pathologie}, new try.\n\n")

                driver.refresh()

            except NoSuchElementException as error:
                print(str(error).split("Stacktrace:")[0])
                print(f"Error from {self.uid}, pathologie: {self.pathologie}, new try.\n\n")

                driver.refresh()

        time.sleep(5)
        driver.quit()

        file_count = len(
            [entry for entry in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, entry))])

        # Après 15 secondes la récupération des articles et relancé
        count = 0
        while file_count < articles_files_count:
            time.sleep(0.5)
            count += 1
            if count == 50:
                print("The number of file. is not equal to what he should be, articles retrieve will restart.\n"
                      "If this problem persist using PubmedGroup class try to reduce threading threadingObject parameters (default = 3\n"
                      "Else increase time.sleep or count max from RetrieveArticles Pubmed method.")
                self.RetrieveArticles()

        self.dataframes = self._UnifyFiles()

        shutil.rmtree(self.directory)

        if self.dataframes.shape[0] < total_results:
            print(f"Missing articles for object with uid: {self.uid}, pathologie: {self.pathologie}, new try.")
            self.RetrieveArticles()

# Ensemble des actions réalisées par Selenium
    def _SeleniumActions(self, _driver):

        open_save_window = _driver.find_element(by=By.ID, value='save-results-panel-trigger')
        open_save_window.click()

        time.sleep(self.delay)

        select_result = Select(_driver.find_element(by=By.ID, value='save-action-selection'))
        select_result.select_by_visible_text('All results')

        time.sleep(self.delay)

        select_format = Select(_driver.find_element(by=By.ID, value='save-action-format'))
        select_format.select_by_visible_text('PubMed')

        time.sleep(self.delay)

        save_button = _driver.find_element(by=By.CLASS_NAME, value='action-panel-submit')
        _driver.execute_script("arguments[0].click();", save_button)

    def _UnifyFiles(self):

        dataframe_list = self._TransformTxtToDataframe()

        final_df = None
        for df in dataframe_list:
            if final_df is None:
                final_df = df
            else:
                final_df = pd.concat([final_df, df])

        final_df = final_df.rename(
            columns={col: Pubmed.tag_translation[col] for col in final_df.columns}).drop_duplicates().reset_index(
            drop=True)

        return final_df

    def _TransformTxtToDataframe(self):

        object_files = glob.glob(f"{self.directory}/*.txt") if platform.system() == "Linux" else glob.glob(
            f"{self.directory}\\*.txt")
        dataframe_list = []

        for file in object_files:
            file = open(file, "r", encoding='utf-8').read()

            self.dictionary = {"AB": [], "AD": [], "AID": [], "DP": [], "FAU": [], "IR": [], "JT": [], "MH": [],
                               "OT": [],
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

#
#
# Les méthodes ci-dessous servent à l'initialisation de l'objet:
#    - InitializeObjectVariables : ensembles des variables/paramètres
#
#    - InitializeURL : créer la base de l'url de l'objet
#
#    - InitializeSelenium : initialisation et configuration du moteur de recherche (ici chrome), pour utiliser selenium
#      il faut générer un jeton API via les paramètres développeurs de github.
#
#

    def __InitializeObjectVariables__(self, pathologie: str, delay: float):
        self.uid = uuid4().hex
        self.directory = f"{os.path.abspath(os.curdir)}/data/temp/{self.uid}"
        self.directory = self.directory if platform.system() == "Linux" else self.directory.replace("/", "\\")
        self.pathologie = pathologie
        self.dataframes = pd.DataFrame()
        self.delay = delay

    def __InitializeURL__(self, filters: list):
        url = f"https://pubmed.ncbi.nlm.nih.gov/?term={Pubmed.default_pathologies[self.pathologie] if self.pathologie in Pubmed.default_pathologies.keys() else self.pathologie}&filter=dates.2000%2F1%2F1-{str(datetime.now().year)}%2F12%2F31"

        if filters is None:
            pass

        elif isinstance(filters, list):
            for value in filters:
                value = str(value).lower().strip()

                if value not in Pubmed.valid_filter.keys():
                    raise ValueError

                url += f"&filter={Pubmed.valid_filter[value]}"

        print(url)
        self.url = url

    def __InitializeSelenium__(self):
        os.environ["GH_TOKEN"] = "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"
        self.service = Service(executable_path=ChromeDriverManager().install())
        self.options = Options()
        self.options.add_argument("--disable-notifications")
        prefs = {"download.default_directory": self.directory}
        self.options.add_experimental_option("prefs", prefs)

    all_tag = ["PMID", "OWN", "STAT", "DCOM", "LR", "IS", "VI", "DP", "TI", "PG", "LID", "AB", "CI", "FAU",
               "AU", "AD", "LA", "PT", "DEP", "PL", "TA", "JT", "JID", "SB", "MH", "OTO", " OT", "EDAT", "MHDA",
               "CRDT", "PHST", "AID", "PST", "SO"]

    valid_tag = ["AB", "AD", "AID", "DP", "FAU", "IR", "JT", "MH", "OT", "PL", "PMID", "PT", "RN", "TI"]

    tag_translation = {"AB": "Abstract", "AD": "Affiliation", "AID": "Article_identifier",
                       "DP": "Publication_date", "FAU": "Full_author_name", "IR": "Investigator",
                       "JT": "Full_journal", "MH": "Mesh_terms", "OT": "Other_term",
                       "PL": "Place_of_publication", "PMID": "PMID", "PT": "Publication_type",
                       "RN": "Chemical", "TI": "Title"}

    default_pathologies = {
        "hyperthyroidie": "((((((((((hyperthyroidism[MeSH Terms]) OR (hyperthyroidism[Text Word])) OR (hyperthyroid[Text Word])) OR (graves disease[MeSH Terms])) OR (graves disease[Text Word])) OR (basedow[Text Word])) OR (thyrotoxicosis[MeSH Terms])) OR (thyrotoxicosis[Text Word])) OR (thyroid crisis[Text Word])) OR (crisis thyroid[Text Word])) OR (thyroid crisis[MeSH Terms])",
        "hypothyroidie": "%28%28%28%28%28%28%28%28%28%28%28hypothyroidism%5BMeSH+Terms%5D%29+OR+%28hypothyroidism%5BText+Word%5D%29%29+OR+%28congenital+hypothyroidism%5BMeSH+Terms%5D%29%29+OR+%28cretinism%5BText+Word%5D%29%29+OR+%28%22congenital+iodine+deficiency+syndrome%22%5BText+Word%5D%29%29+OR+%28lingual+thyroid%5BMeSH+Terms%5D%29%29+OR+%28%22thyroid+dysgenesis%22%5BText+Word%5D%29%29+OR+%28%22lingual+thyroid%22%5BText+Word%5D%29%29+OR+%28%22thyroid+lingual%22%5BText+Word%5D%29%29+OR+%28lingual+goiter%5BMeSH+Terms%5D%29%29+OR+%28%22lingual+goiter%22%5BText+Word%5D%29%29+OR+%28%22goiter+lingual%22%5BText+Word%5D%29",
        "goitre": "%28%28goiter%5BMeSH+Terms%5D%29+OR+%28goiter%5BText+Word%5D%29+OR+%28goiters%5BText+Word%5D%29%29+OR+%28%28goiter%2C+nodular%5BMeSH+Terms%5D%29+OR+%28%22nodular+goiters%22%5BText+Word%5D%29+OR+%28%22nodular+goiter%22%5BText+Word%5D%29+OR+%28%22goiter%2C+nodular%22%5BText+Word%5D%29%29",
        "thyroidites": "%28%28%28%28%28%28%28%28%28%28%28thyroiditis%2C+autoimmune%5BMeSH+Terms%5D%29+OR+%28thyroiditis%5BText+Word%5D%29%29+OR+%28hashimoto+disease%5BMeSH+Terms%5D%29%29+OR+%28hashimoto%5BText+Word%5D%29%29%29+OR+%28postpartum+thyroiditis%5BMeSH+Terms%5D%29%29+OR+%28%22postpartum+thyroiditis%22%5BText+Word%5D%29%29+OR+%28thyroiditis%2C+subacute%5BMeSH+Terms%5D%29%29+OR+%28%22thyroiditis%2C+subacute%22%5BText+Word%5D%29%29+OR+%28%22subacute+thyroiditis%22%5BText+Word%5D%29%29+OR+%28%22subacute+thyroiditis%22%5BText+Word%5D%29%29+OR+%28thyroiditis%2C+suppurative%5BMeSH+Terms%5D%29",
        "thyroid neoplasm": "%28%28%28%28%28%28%28%28%28thyroid+neoplasms%5BMeSH+Terms%5D%29+OR+%28thyroid+neoplasms%5BText+Word%5D%29%29+OR+%28thyroid+neoplasm%5BText+Word%5D%29%29+OR+%28thyroid+cancer%5BText+Word%5D%29%29+OR+%28thyroid+carcinoma%5BText+Word%5D%29%29+OR+%28thyroid+cancers%5BText+Word%5D%29%29+OR+%28cancer+of+thyroid%5BText+Word%5D%29%29+OR+%28cancer+of+the+thyroid%5BText+Word%5D%29%29+OR+%28thyroid+carcinomas%5BText+Word%5D%29%29+OR+%28thyroid+carcinoma%2C+anaplastic%5BMeSH+Terms%5D%29",
        "euthyroid sick syndromes": "%28%22euthyroid+sick+syndromes%22%5BMeSH+Terms%5D+OR+%22euthyroid+sick+syndrome%22%5BText+Word%5D+OR+%22low+t3+syndrome%22%5BText+Word%5D+OR+%22euthyroid+sick+syndromes%22%5BText+Word%5D+OR+%22low+t3+low+t4+syndrome%22%5BText+Word%5D+OR+%22syndrome+non+thyroidal+illness%22%5BText+Word%5D+OR+%22high+t4+syndrome%22%5BText+Word%5D+OR+%22low+t3+and+low+t4+syndrome%22%5BText+Word%5D+OR+%22sick+euthyroid+syndrome%22%5BText+Word%5D+OR+%22non-thyroidal+illness+syndrome%22%5BText+Word%5D+OR+%22low+t3+low+t4+syndrome%22%5BText+Word%5D+OR+%22non-thyroidal+illness+syndrome%22%5BText+Word%5D%29",
        "hyperthyroxinemia": "%28%22hyperthyroxinemia%22%5BMeSH+Terms%5D+OR+%22hyperthyroxinemias%22%5BText+Word%5D+OR+%22hyperthyroxinemia%22%5BText+Word%5D+OR+%22thyroid+hormone+resistance+syndrome%22%5BMeSH+Terms%5D+OR+%22thyroid+hormone+resistance+syndrome%22%5BText+Word%5D+OR+%22generalized+resistance+to+thyroid+hormone%22%5BText+Word%5D+OR+%22hyperthyroxinemia%2C+familial+dysalbuminemic%22%5BMeSH+Terms%5D%29%29",
        "thyroid nodule": "%28%28%28%28%28%22thyroid+nodule%22%5BMH%5D+OR+%28%22nodules%2C+thyroid%22%5BTW%5D+OR+%22thyroid+nodules%22%5BTW%5D+OR+%22thyroid+nodule%22%5BTW%5D+OR+%22nodule%2C+thyroid%22%5BTW%5D%29%29%29%29%29+OR+%28%28%22thyroid+nodule%22%5BMH%5D+OR+%28%22nodules%2C+thyroid%22%5BTW%5D+OR+%22thyroid+nodules%22%5BTW%5D+OR+%22thyroid+nodule%22%5BTW%5D+OR+%22nodule%2C+thyroid%22%5BTW%5D%29%29%29%29",
        "thyroid disease": "%28%28%28%28%28%22thyroid+diseases%22%5BMH%5D+OR+%28%22thyroid+disease%22%5BTW%5D+OR+%22disease%2C+thyroid%22%5BTW%5D+OR+%22diseases%2C+thyroid%22%5BTW%5D+OR+%22thyroid+diseases%22%5BTW%5D%29%29%29%29%29+OR+%28%28%22thyroid+diseases%22%5BMH%5D+OR+%28%22thyroid+disease%22%5BTW%5D+OR+%22disease%2C+thyroid%22%5BTW%5D+OR+%22diseases%2C+thyroid%22%5BTW%5D+OR+%22thyroid+diseases%22%5BTW%5D%29%29%29%29",
    }

    valid_filter = {"humans": "hum_ani.humans",
                    "abstract": "simsearch1.fha",
                    "free full text": "simsearch2.ffrft",
                    "full text": "simsearch3.fft",
                    "associated data": "articleattr.data",
                    "books and documents": "pubt.booksdocs",
                    "clinical trial": "pubt.clinicaltrial",
                    "meta-analysis": "pubt.meta-analysis",
                    "randomized controlled trial": "pubt.randomizedcontrolledtrial",
                    "review": "pubt.review",
                    "systematic review": "pubt.systematicreview"}

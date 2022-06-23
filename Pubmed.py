import pandas as pd

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
        total_results = int(driver.find_element(by=By.CLASS_NAME, value="value").text.replace(",", ""))
        download_count = 0
        year_range = [2000, 2001]

        while year_range[1] <= datetime.now().year + 2:

            # Met à jour les dates de l'url
            driver.get(re.sub(r"dates.\d{4}%2F1%2F1-\d{4}", f"dates.{year_range[0]}%2F1%2F1-{year_range[1]}", self.url))

            try:
                self._SeleniumActions(driver)
                year_range = [x + 2 for x in year_range]
                download_count += 1

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

        file_count = len([file for file in glob.glob(f"{self.directory}/*.txt")])

        # Après 15 secondes la récupération des articles et relancé
        count = 0
        while file_count < download_count:
            file_count = len([file for file in glob.glob(f"{self.directory}/*.txt")])
            print(f'{self.pathologie}: {file_count}, {download_count}')
            time.sleep(1)
            count += 1
            if count == 120:
                print("The number of file. is not equal to what he should be, articles retrieve will restart.\n"
                      "If this problem persist using PubmedGroup class try to reduce threading threadingObject parameters (default = 3)\n"
                      "Else increase time.sleep or count max from RetrieveArticles Pubmed method.")
                shutil.rmtree(self.directory)
                driver.quit()
                self.directory = f"{os.path.abspath(os.curdir)}/data/temp/{self.uid}"
                self.directory = self.directory if platform.system() == "Linux" else self.directory.replace("/", "\\")
                self.RetrieveArticles()
                break

        if self.is_already_done:
            return None

        driver.quit()

        dataframe = self._UnifyFiles()
        dataframe = self._ArticleIdentifiersSplit(dataframe)
        dataframe = self._ArticlesClassification(dataframe)
        dataframe = self._ObservationalStudyCharacteristics(dataframe)
        self.dataframes = dataframe

        shutil.rmtree(self.directory)

        if self.dataframes.shape[0] < total_results:
            print(self.dataframes.shape[0], total_results)
            print(f"Missing articles for object with uid: {self.uid}, pathologie: {self.pathologie}, new try.")
            self.RetrieveArticles()

        self.is_already_done = True

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
                    last_tag = name_tag if name_tag in Pubmed.all_tag else last_tag

                    if name_tag not in Pubmed.valid_tag:
                        if name_tag not in Pubmed.all_tag and last_tag in Pubmed.valid_tag:
                            if last_tag == "AD":
                                article_dictionary["FAU"] += f" {name_tag.lower()}"
                            else:
                                article_dictionary[last_tag] += f" {name_tag.lower()}"
                        else:
                            continue
                    elif last_tag == "AD":
                        article_dictionary["FAU"] += "/SPLIT/" + tag[1].lower()
                    else:
                        article_dictionary[name_tag] += tag[1].lower() if len(article_dictionary[name_tag]) < 1 else "---" + \
                                                                                                             tag[1].lower()
                        last_tag = name_tag

                for k, v in article_dictionary.items():
                    self.dictionary[k].append(v)

            df = pd.DataFrame(self.dictionary)
            dataframe_list.append(df)

        return dataframe_list

    def _ArticleIdentifiersSplit(self, df: pd.DataFrame):
        for column in self.col_str_to_list:
            df[column] = df[column].apply(lambda x: x.lower().split("---") if isinstance(x, str) else x)

        df["PII"] = df["Article_identifier"].apply(lambda x: self._DoiOrPii(x, "pii"))
        df["DOI"] = df["Article_identifier"].apply(lambda x: self._DoiOrPii(x, "doi"))

        return df

    @staticmethod
    def _DoiOrPii(value_list: list, choice: str):

        if value_list is None:
            return None

        choice = choice.lower().strip()

        for identifier in value_list:
            if choice in identifier:
                return identifier.replace(f"[{choice}]", "")

        return None

    @staticmethod
    def _ArticlesClassification(df: pd.DataFrame):
        df["Condition"] = df.Abstract.apply(lambda x: [])
        for idx in df.index:

            for category, terms_list in Pubmed.category.items():

                for term in terms_list:

                    if term in df.loc[idx, "Title"]:
                        df.loc[idx, "Condition"].append(term)
                        continue

                    if term in df.loc[idx, "Abstract"] and category != "thyroid disease":
                        df.loc[idx, "Condition"].append(term)
                        continue

                    for mesh_terms in df.loc[idx, 'Mesh_terms']:
                        mesh_term_without_slash = mesh_terms.replace("*", "").split("/")
                        mesh_term_without_slash = [x.strip() for x in mesh_term_without_slash]

                        if term in mesh_term_without_slash:
                            df.loc[idx, "Condition"].append(term)
                            break

                    for mesh_terms in df.loc[idx, "Other_term"]:
                        mesh_term_without_slash = mesh_terms.replace("*", "").split("/")

                        if term in mesh_term_without_slash:
                            df.loc[idx, "Condition"].append(term)
                            break

        return df

    @staticmethod
    def _ObservationalStudyCharacteristics(df: pd.DataFrame):
        df["Observational_study_characteristics"] = df.Abstract.apply(lambda x: [])

        for idx in df.index:

            for term in Pubmed.observational_study_characteristics:

                if term in df.loc[idx, "Title"]:
                    df.loc[idx, "Observational_study_characteristics"].append(term)
                    continue

                if term in df.loc[idx, "Abstract"]:
                    df.loc[idx, "Observational_study_characteristics"].append(term)
                    continue

                for mesh_terms in df.loc[idx, 'Mesh_terms']:
                    mesh_term_without_slash = mesh_terms.replace("*", "").split("/")
                    mesh_term_without_slash = [x.strip() for x in mesh_term_without_slash]

                    if term in mesh_term_without_slash:
                        df.loc[idx, "Observational_study_characteristics"].append(term)
                        break

                for mesh_terms in df.loc[idx, "Other_term"]:
                    mesh_term_without_slash = mesh_terms.replace("*", "").split("/")

                    if term in mesh_term_without_slash:
                        df.loc[idx, "Observational_study_characteristics"].append(term)
                        break

        return df

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
        self.is_already_done = False
        self.delay = delay

    def __InitializeURL__(self, filters: list):
        url = f"https://pubmed.ncbi.nlm.nih.gov/?term={Pubmed.default_pathologies[self.pathologie] if self.pathologie in Pubmed.default_pathologies.keys() else self.pathologie}&filter=dates.2000%2F1%2F1-{str(datetime.now().year)}%2F12%2F31"

        if isinstance(filters, list):
            for value in filters:
                value = str(value).lower().strip()

                if value not in Pubmed.valid_filter.keys():
                    raise ValueError

                url += f"&filter={Pubmed.valid_filter[value]}"

        self.url = url

    def __InitializeSelenium__(self):
        os.environ["GH_TOKEN"] = "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"
        self.service = Service(executable_path=ChromeDriverManager().install())
        self.options = Options()
        self.options.add_argument("--disable-notifications")
        prefs = {"download.default_directory": self.directory}
        self.options.add_experimental_option("prefs", prefs)

    all_tag = ["AB", "AD", "AID", "AU", "BTI", "CI", "CIN", "CN", "COI", "CON", "CP", "CRDT", "CRF", "CRI", "CTDT", "CTI",
               "DCOM", "DDIN", "DRIN", "DEP", "DP", "DRDT", "ECF", "ECI", "EDAT", "EFR", "EIN", "ED", "EN", "FAU", "FED", "FIR",
               "FPS", "GN", "GR", "GS", "IP", "IR", "IRAD", "IS", "ISBN", "JID", "JT", "LA", "LID", "LR", "MH", "MHDA",
               "OAB", "OABL", "OCI", "OID", "ORI", "OT", "OTO", "OWN", "PB", "PG", "PHST", "PL", "PMCR", "PMID", "PS", "PST",
               "PT", "RF", "RIN", "RN", "ROF", "RPF", "RPI", "RRI", "RRF", "SB", "SFM", "SI", "SO", "SPIN", "STAT", "TA", "TI",
               "TT", "UIN", "UOF", "VI", "VTI"]

    valid_tag = ["AB", "AD", "AID", "DP", "FAU", "IR", "JT", "MH", "OT", "PL", "PMID", "PT", "RN", "TI"]

    tag_translation = {"AB": "Abstract", "AD": "Affiliation", "AID": "Article_identifier",
                       "DP": "Publication_date", "FAU": "Full_author_name", "IR": "Investigator",
                       "JT": "Full_journal", "MH": "Mesh_terms", "OT": "Other_term",
                       "PL": "Place_of_publication", "PMID": "PMID", "PT": "Publication_type",
                       "RN": "Chemical", "TI": "Title"}

    default_pathologies = {
        "hyperthyroidie": "((((((((((hyperthyroidism[MeSH Terms]) OR (hyperthyroidism[Text Word])) OR (hyperthyroid[Text Word])) OR (graves disease[MeSH Terms])) OR (graves disease[Text Word])) OR (basedow[Text Word])) OR (thyrotoxicosis[MeSH Terms])) OR (thyrotoxicosis[Text Word])) OR (thyroid crisis[Text Word])) OR (crisis thyroid[Text Word])) OR (thyroid crisis[MeSH Terms])",
        "hypothyroidie": "(((((((((((hypothyroidism[MeSH Terms]) OR (hypothyroidism[Text Word])) OR (congenital hypothyroidism[MeSH Terms])) OR (cretinism[Text Word])) OR (congenital iodine deficiency syndrome[Text Word])) OR (lingual thyroid[MeSH Terms])) OR (thyroid dysgenesis[Text Word])) OR (lingual thyroid[Text Word])) OR (thyroid lingual[Text Word])) OR (lingual goiter[MeSH Terms])) OR (lingual goiter[Text Word])) OR (goiter lingual[Text Word])",
        "goitre": "((goiter[MeSH Terms]) OR (goiter[Text Word]) OR (goiters[Text Word])) OR ((goiter, nodular[MeSH Terms]) OR (nodular goiters[Text Word]) OR (nodular goiter[Text Word]) OR (goiter, nodular[Text Word]))",
        "thyroidites": "(((((((((((thyroiditis, autoimmune[MeSH Terms]) OR (thyroiditis[Text Word])) OR (hashimoto disease[MeSH Terms])) OR (hashimoto[Text Word]))) OR (postpartum thyroiditis[MeSH Terms])) OR (postpartum thyroiditis[Text Word])) OR (thyroiditis, subacute[MeSH Terms])) OR (thyroiditis, subacute[Text Word])) OR (subacute thyroiditis[Text Word])) OR (subacute thyroiditis[Text Word])) OR (thyroiditis, suppurative[MeSH Terms])",
        "thyroid neoplasm": "(((((((((thyroid neoplasms[MeSH Terms]) OR (thyroid neoplasms[Text Word])) OR (thyroid neoplasm[Text Word])) OR (thyroid cancer[Text Word])) OR (thyroid carcinoma[Text Word])) OR (thyroid cancers[Text Word])) OR (cancer of thyroid[Text Word])) OR (cancer of the thyroid[Text Word])) OR (thyroid carcinomas[Text Word])) OR (thyroid carcinoma, anaplastic[MeSH Terms])",
        "euthyroid sick syndromes": "(euthyroid sick syndromes[MeSH Terms] OR euthyroid sick syndrome[Text Word] OR low t3 syndrome[Text Word] OR euthyroid sick syndromes[Text Word] OR low t3 low t4 syndrome[Text Word] OR syndrome non thyroidal illness[Text Word] OR high t4 syndrome[Text Word] OR low t3 and low t4 syndrome[Text Word] OR sick euthyroid syndrome[Text Word] OR non-thyroidal illness syndrome[Text Word] OR low t3 low t4 syndrome[Text Word] OR non-thyroidal illness syndrome[Text Word])",
        "hyperthyroxinemia": "(hyperthyroxinemia[MeSH Terms] OR hyperthyroxinemias[Text Word] OR hyperthyroxinemia[Text Word] OR thyroid hormone resistance syndrome[MeSH Terms] OR thyroid hormone resistance syndrome[Text Word] OR generalized resistance to thyroid hormone[Text Word] OR hyperthyroxinemia, familial dysalbuminemic[MeSH Terms]))",
        "thyroid nodule": "(((((thyroid nodule[MH] OR (nodules, thyroid[TW] OR thyroid nodules[TW] OR thyroid nodule[TW] OR nodule, thyroid[TW]))))) OR ((thyroid nodule[MH] OR (nodules, thyroid[TW] OR thyroid nodules[TW] OR thyroid nodule[TW] OR nodule, thyroid[TW]))))",
        "parathyroid diseases": "(((((((((((((((((parathyroid diseases[MeSH Terms]) OR (parathyroid diseases[Text Word])) OR (parathyroid disease[Text Word])) OR (parathyroid disorder[Text Word])) OR (parathyroid disorders[Text Word])) OR (hyperparathyroidism[MeSH Terms])) OR (hyperparathyroidism[Text Word])) OR (hypoparathyroidism[MeSH Terms])) OR (hypoparathyroidism[Text Word])) OR (parathyroid neoplasms[MeSH Terms])) OR (parathyroid neoplasms[Text Word])) OR (parathyroid adenoma[Text Word])) OR (parathyroid cancers[Text Word])) OR (parathyroid cancer[Text Word])) OR (parathyroid carcinomas[Text Word])) OR (cancer of parathyroid[Text Word])) OR (parathyroid neoplasm[Text Word])) OR (parathyroid carcinoma[Text Word])",
        "thyroid disease": "(((((thyroid diseases[MH] OR (thyroid disease[TW] OR disease, thyroid[TW] OR diseases, thyroid[TW] OR thyroid diseases[TW]))))) OR ((thyroid diseases[MH] OR (thyroid disease[TW] OR disease, thyroid[TW] OR diseases, thyroid[TW] OR thyroid diseases[TW]))))",
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

    col_str_to_list = ["Article_identifier", "Full_author_name", "Mesh_terms", "Publication_type", "Chemical"]

    category = {
        "euthyroid sick syndromes": ["euthyroid sick syndromes"],
        "goiter": ["goiter", "goiter, endemic", "goiter, nodular", "goiter, substernal", "lingual goiter"],
        "hyperthyroidism": ["hyperthyroidism", "graves disease", "graves' disease", "graves ophthalmopathy", "thyrotoxicosis", "thyroid crisis"],
        "hyperthyroxinemia": ["hyperthyroxinemia", "hyperthyroxinemia, familial dysalbuminemic", "thyroid hormone resistance syndrome"],
        "hypothyroidism": ["congenital hypothyroidism", "thyroid dysgenesis", "lingual thyroid", "lingual goiter", "hypothyroidism"],
        "thyroid neoplasms": ["thyroid neoplasms", "thyroid cancer, papillary", "thyroid carcinoma, anaplastic"],
        "thyroid nodule": ["thyroid nodule"],
        "thyroiditis": ["thyroiditis, autoimmune", "hashimoto disease", "postpartum thyroiditis", "thyroiditis, subacute", "thyroiditis, suppurative"],
        "thyroid disease": ["thyroid disease", "thyroid diseases"]
    }

    observational_study_characteristics = ["case-control studies", "retrospective studies", "cohort studies", "follow-up studies",
                                           "longitudinal studies", "prospective studies", "controlled before-after studies", "cross-sectional studies",
                                           "historically controlled study", "interrupted time series analysis", "case-control", "retrospective", "cohort",
                                           "longitudinal", "prospective", "cross-sectional"]
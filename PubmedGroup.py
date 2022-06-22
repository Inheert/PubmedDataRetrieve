from Pubmed import *

class PubmedGroup:

    directory = f"{os.path.abspath(os.curdir)}/data"
    col_str_to_list = ["Article_identifier", "Full_author_name", "Mesh_terms", "Publication_type", "Chemical", "Condition",
                       "Observational_study_characteristics"]

    population_terms = ["child", "infant, newborn", "infant", "child, preschool", "postmenopause", "adolescent",
                        "adult", "young adult", "pregnant women", "middle aged", "aged", "aged, 80 and over",
                        "male", "female"]

    category = {
        "euthyroid sick syndromes": ["euthyroid sick syndromes"],
        "goiter": ["goiter", "goiter, endemic", "goiter, nodular", "goiter, substernal", "lingual goiter"],
        "hyperthyroidism": ["hyperthyroidism", "graves disease", "graves' disease", "graves ophthalmopathy", "thyrotoxicosis", "thyroid crisis"],
        "hyperthyroxinemia": ["hyperthyroxinemia", "hyperthyroxinemia, familial dysalbuminemic", "thyroid hormone resistance syndrome"],
        "hypothyroidism": ["congenital hypothyroidism", "thyroid dysgenesis", "lingual thyroid", "lingual goiter", "hypothyroidism"],
        "thyroid neoplasms": ["thyroid neoplasms", "thyroid cancer, papillary", "thyroid carcinoma, anaplastic"],
        "thyroid nodule": ["thyroid nodule"],
        "thyroiditis": ["thyroiditis, autoimmune", "hashimoto disease", "postpartum thyroiditis", "thyroiditis, subacute", "thyroiditis, suppurative"],
        "thyroid disease": ["thyroid disease"]
    }

    def __init__(self, pathologies: list, filters: list = None, threadingObject: int = 3, delay: float = 1):

        self.dataframes = {}
        self.PubmedObject = [Pubmed(x, filters, delay) for x in pathologies]
        self.threading_list = [threading.Thread(target=obj.RetrieveArticles) for obj in self.PubmedObject]
        self.threadingObject = threadingObject

    def StartRetrieve(self):

        threading_split = []

        count = 0
        thread = []
        for obj in self.threading_list:
            if count < self.threadingObject:
                thread.append(obj)

            elif count == self.threadingObject:
                threading_split.append(thread)
                count = 0
                thread = [obj]
            count += 1

        if len(thread) >= 1:
            threading_split.append(thread)

        print(datetime.now())
        for sub_list in threading_split:
            for obj in sub_list:
                obj.start()
            for obj in sub_list:
                obj.join()
        print(datetime.now())

    def JoinAndCleanDataframe(self):

        final_df = None
        dataframe_list = [df.dataframes for df in self.PubmedObject]

        for df in dataframe_list:
            if final_df is None:
                final_df = df
            final_df = pd.concat([final_df, df])

        self._DataframeSaveAndSplit(final_df, self.col_str_to_list)

    def _DataframeSaveAndSplit(self, dataframe: pd.DataFrame, new_dataframe: list):

        dataframe = dataframe.reset_index(drop=True)

        self.dataframes["pubmedArticles"] = dataframe

        for column in new_dataframe:
            self.dataframes[column] = self.dataframes["pubmedArticles"][["PMID", column]].explode(column)
            self.dataframes[column] = self.dataframes[column].drop_duplicates()
            self.dataframes[column] = self.dataframes[column].dropna()

            if column == "Chemical":
                self.dataframes[column][column] = self.dataframes[column][column].apply(
                    lambda x: re.findall(r"\(([^)]+)\)", x)[0] if len(re.findall(r"\(([^)]+)\)", x)) != 0 else x)
            elif column == "Condition":
                self.dataframes[column]["Category"] = self.dataframes[column][column].apply(lambda x: self._GetCategoryCondition(x))

            self.dataframes[column].to_csv(f"{PubmedGroup.directory}/{column}.csv")

            self._CreateNewDataframes("population", column)

        self.dataframes["pubmedArticles"] = self.dataframes["pubmedArticles"].drop(columns=[col for col in PubmedGroup.col_str_to_list])
        self.dataframes["pubmedArticles"] = self.dataframes["pubmedArticles"].drop_duplicates()

        self.dataframes["pubmedArticles"].to_csv(f"{PubmedGroup.directory}/pubmedArticles.csv")

    def _CreateNewDataframes(self, newCol, column):
        if newCol == "population" and column == "Mesh_terms":

            df = self.dataframes["Mesh_terms"].copy()

            df["Population"] = df["Mesh_terms"].apply(lambda x: x if x in PubmedGroup.population_terms else None)
            df.dropna(subset="Population", inplace=True)

            self.dataframes["Population"] = df[["PMID", "Population"]]
            self.dataframes["Population"].to_csv(f"{PubmedGroup.directory}/{'Population'}.csv")

    @staticmethod
    def _GetCategoryCondition(pathologie):
        for k, v in Pubmed.category.items():
            if pathologie in v:
                return k

    def GetInfos(self):
        str_pathos = ""
        for patho in Pubmed.default_pathologies.keys():
            str_pathos += f", {patho}"

        str_filters = ""
        for filter in Pubmed.valid_filter:
            str_filters += f", {filter}"

        print(f"Total instance: {len(self.threading_list)}")
        print(f"Threading count: {self.threadingObject}")
        print("")
        print(f"Default pathologies: {str_pathos}")
        print(f"available filters: {str_filters}")

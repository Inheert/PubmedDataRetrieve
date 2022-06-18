from Pubmed import *

class PubmedGroup:

    directory = f"{os.path.abspath(os.curdir)}/data"
    col_str_to_list = ["Article_identifier", "Full_author_name", "Mesh_terms", "Publication_type", "Chemical"]

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

        final_df.drop_duplicates(inplace=True)

        for column in self.col_str_to_list:
            final_df[column] = final_df[column].apply(lambda x: x.split("---") if isinstance(x, str) else None)

        final_df["PII"] = final_df["Article_identifier"].apply(lambda x: PubmedGroup._DoiOrPii(x, "pii"))
        final_df["DOI"] = final_df["Article_identifier"].apply(lambda x: PubmedGroup._DoiOrPii(x, "doi"))

        self._DataframeSaveAndSplit(final_df, self.col_str_to_list)

    @staticmethod
    def _DoiOrPii(value_list: list, choice: str):

        if value_list is None:
            return None

        choice = choice.lower().strip()

        for identifier in value_list:
            if choice in identifier:
                return identifier.replace(f"[{choice}]", "")

        return None

    def _DataframeSaveAndSplit(self, dataframe: pd.Series, new_dataframe: list):

        self.dataframes["pubmedArticles"] = dataframe
        dataframe.to_csv(f"{PubmedGroup.directory}/pubmedArticles.csv")

        for column in new_dataframe:
            self.dataframes[column] = dataframe[["PMID", column]].explode(column)
            self.dataframes[column].to_csv(f"{PubmedGroup.directory}/{column}.csv")

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

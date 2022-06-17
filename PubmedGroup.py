import threading
import pandas as pd
import os
from Pubmed import Pubmed
import time
from datetime import datetime

class PubmedGroup:

    directory = f"{os.path.abspath(os.curdir)}/data"

    def __init__(self, pathologies: list):

        self.dataframes = {}
        self.pathologies = [Pubmed(x) for x in pathologies]
        self.threading = [threading.Thread(target=obj.RetrieveArticles) for obj in self.pathologies]

    def StartRetrieve(self):

        threading_split = []

        count = 0
        thread = []
        for obj in self.threading:
            if count < 3:
                thread.append(obj)
            elif count == 3:
                threading_split.append(thread)
                count = 0
                thread = [obj]
            count += 1

        print(datetime.now())
        for sub_list in threading_split:
            for obj in sub_list:
                obj.start()
            for obj in sub_list:
                obj.join()
        print(datetime.now())

        # print(datetime.now())
        # for obj in self.threading:
        #     obj.start()
        # for obj in self.threading:
        #     obj.join()
        # print(datetime.now())

    def JoinAndCleanDataframe(self):

        final_df = None
        dataframe_list = [df.final_dataframe for df in self.pathologies]

        for df in dataframe_list:
            if final_df is None:
                final_df = df

            final_df = pd.concat([final_df, df])

        final_df.drop_duplicates(inplace=True)

        # final_df[["PII", "DOI"]] = final_df["Article_identifier"].str.split("---", n=1, expand=True) if final_df["Article_identifier"] is not None else None

        col_str_to_list = ["Article_identifier", "Full_author_name", "Mesh_terms", "Publication_type", "Chemical"]
        for column in col_str_to_list:
            final_df[column] = final_df[column].apply(lambda x: x.split("---") if isinstance(x, str) else None)

        # final_df["Article_identifier"] = final_df["Article_identifier"].apply(
        #     lambda x: x.split("---") if isinstance(x, str) else None)
        # final_df["Full_author_name"] = final_df["Full_author_name"].apply(
        #     lambda x: x.split("---") if isinstance(x, str) else None)
        # final_df["Mesh_terms"] = final_df["Mesh_terms"].apply(
        #     lambda x: x.split("---") if isinstance(x, str) else None)
        # final_df["Publication_type"] = final_df["Publication_type"].apply(
        #     lambda x: x.split("---") if isinstance(x, str) else None)
        # final_df["Chemical"] = final_df["Chemical"].apply(
        #     lambda x: x.split("---") if isinstance(x, str) else None)

        final_df["PII"] = final_df["Article_identifier"].apply(lambda x: PubmedGroup._DoiOrPii(x, "pii"))
        final_df["DOI"] = final_df["Article_identifier"].apply(lambda x: PubmedGroup._DoiOrPii(x, "doi"))
        self._DataframeSaveAndSplit(final_df)

    @staticmethod
    def _DoiOrPii(value_list: list, choice: str):

        if value_list is None:
            return None

        choice = choice.lower().strip()

        for identifier in value_list:
            if choice in identifier:
                return identifier.replace(f"[{choice}]", "")
        return None

    def _DataframeSaveAndSplit(self, dataframe: pd.Series):

        self.dataframes["pubmedArticles"] = dataframe
        dataframe.to_csv(f"{PubmedGroup.directory}/pubmedArticles.csv")

        self.dataframes["Full_author_name"] = dataframe[["PMID", "Full_author_name"]].explode("Full_author_name")
        self.dataframes["Full_author_name"].to_csv(f"{PubmedGroup.directory}/Full_author_name.csv")

        self.dataframes["Mesh_terms"] = dataframe[["PMID", "Mesh_terms"]].explode("Mesh_terms")
        self.dataframes["Mesh_terms"] .to_csv(f"{PubmedGroup.directory}/Mesh_terms.csv")

        self.dataframes["Publication_type"] = dataframe[["PMID", "Publication_type"]].explode("Publication_type")
        self.dataframes["Publication_type"] .to_csv(f"{PubmedGroup.directory}/Publication_type.csv")

        self.dataframes["Chemical"] = dataframe[["PMID", "Chemical"]].explode("Chemical")
        self.dataframes["Chemical"] .to_csv(f"{PubmedGroup.directory}/pubmedArticles.csv")


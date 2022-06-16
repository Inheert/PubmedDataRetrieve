import threading
import pandas as pd
import os
from Pubmed import Pubmed
import time
from datetime import datetime

class PubmedGroup:

    def __init__(self, pathologies: list):

        self.dataframes = {}
        self.pathologies = [Pubmed(x) for x in pathologies]
        self.threading = [threading.Thread(target=obj.RetrieveArticles) for obj in self.pathologies]

    def StartRetrieve(self):
        print(datetime.now())
        for obj in self.threading:
            obj.start()
        for obj in self.threading:
            obj.join()
        print(datetime.now())

    def JoinDataframe(self):

        final_df = None
        dataframe_list = [df.final_dataframe for df in self.pathologies]

        for df in dataframe_list:
            if final_df is None:
                final_df = df

            final_df = pd.concat([final_df, df])

        final_df.drop_duplicates(inplace=True)

        final_df[["PII", "DOI"]] = df["Article_identifier"].str.split("---", n=1, expand=True)

        final_df["Full_author_name"] = final_df["Full_author_name"].apply(
            lambda x: x.split("---") if isinstance(x, str) else None)
        final_df["Mesh_terms"] = final_df["Mesh_terms"].apply(
            lambda x: x.split("---") if isinstance(x, str) else None)
        final_df["Publication_type"] = final_df["Publication_type"].apply(
            lambda x: x.split("---") if isinstance(x, str) else None)
        final_df["EC_RN_number"] = final_df["EC_RN_number"].apply(
            lambda x: x.split("---") if isinstance(x, str) else None)

        self.dataframes["pubmedArticles"] = final_df
        self.dataframes["Full_author_name"] = final_df[["PMID", "Full_author_name"]].explode("Full_author_name")
        self.dataframes["Mesh_terms"] = final_df[["PMID", "Mesh_terms"]].explode("Mesh_terms")
        self.dataframes["Publication_type"] = final_df[["PMID", "Publication_type"]].explode("Publication_type")
        self.dataframes["EC_RN_number"] = final_df[["PMID", "EC_RN_number"]].explode("EC_RN_number")

        # self.dataframes.to_csv(f"{os.path.abspath(os.curdir)}/data/pubmedArticles.csv")

    def CreateNewDataframe(self, col, string):

        self.dataframes[col] = self.dataframes
        return string.split("---" if isinstance(string, float) == False else None)



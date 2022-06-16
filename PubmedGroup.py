import threading
import pandas as pd
import os
from Pubmed import Pubmed
import time
from datetime import datetime

class PubmedGroup:

    def __init__(self, pathologies: list):

        self.dataframe = None
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

        self.dataframe = final_df.drop_duplicates()
        self.dataframe.to_csv(f"{os.path.abspath(os.curdir)}/data/pubmedArticles.csv")


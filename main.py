import pandas as pd
from PubMed import *

# first = Pubmed("https://pubmed.ncbi.nlm.nih.gov/?term=%28autoimmune+thyroid+disease%29+AND+%28neplasms%29&filter=hum_ani.humans&filter=years.2000-2022&size=200&page=1")
# second = Pubmed("https://pubmed.ncbi.nlm.nih.gov/?term=%28euthyroid+sick+syndrome%29&size=200")
#
# first.RetrieveArticles()
# first.UnifyFiles()

dictionary = {"AB": [], "AD": [], "AID": [], "DP": [], "FAU": [], "IR": [], "JT": [], "MH": [], "OT": [],
              "PL": [], "PMID": [], "PT": [], "RN": [], "TI": []}

valid = ["AB", "AD", "AID", "DP", "FAU", "IR", "JT", "MH", "OT", "PL", "PMID", "PT", "RN", "TI"]

file = open("data/75e9bfb0f24a4667ae37562c2579a6e2/pubmed-autoimmune-set.txt", "r")
articles = file.read().split("\n\n")

for article in articles:

    article_dictionary = {"AB": "", "AD": "", "AID": "", "DP": "", "FAU": "", "IR": "", "JT": "", "MH": "", "OT": "",
                  "PL": "", "PMID": "", "PT": "", "RN": "", "TI": ""}

    article = article.split("\n")

    for tag in article:
        tag = tag.split("- ")

        if tag[0].strip() not in valid:
            pass
        else:
            # Séparateur non fonctionnel revoir cette partie
            article_dictionary[tag[0].strip()] += tag[1] if len(article_dictionary[tag[0].strip()]) > 1 else "$#$"+tag[1]

    for k, v in article_dictionary.items():
        dictionary[k].append(v)


df = pd.DataFrame(dictionary)
df.to_csv("csv_test.csv")



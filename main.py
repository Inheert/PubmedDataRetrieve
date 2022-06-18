from PubmedGroup import PubmedGroup
"""
heroku chrome: 
https://elements.heroku.com/buildpacks/heroku/heroku-buildpack-google-chrome

Améliorer la gestion probable des erreurs :
    - np articles pb != np articles dataframe
    - 
"""

# first = Pubmed("hyperthyroidie")
# first.RetrieveArticles()

test = PubmedGroup(pathologies=["Hyperthyroidie", "Hypothyroidie", "goitre", "thyroidites", "Euthyroid sick syndromes",
                    "Hyperthyroxinemia", "Thyroid neoplasm", "Thyroid nodule", "Thyroid disease"],
                   filters=["humans"], delay=0.5, threadingObject=5)
test.StartRetrieve()
test.JoinAndCleanDataframe()
print(test.dataframes)


# txt = "https://pubmed.ncbi.nlm.nih.gov/?term={keyword}&filter=hum_ani.humans&filter=years.2000-2001&size=200&page=1"
# new = re.sub(r"years.\d{4}-\d{4}", "year.2010-2011", txt)
# print(new)

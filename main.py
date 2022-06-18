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

test = PubmedGroup(pathologies=["goitre", "thyroidites", "thyroid nodule"],
                   filters=["humans"], threadingObject=5, delay=0.5)
test.StartRetrieve()
test.JoinAndCleanDataframe()
print(test.dataframes)


# txt = "https://pubmed.ncbi.nlm.nih.gov/?term={keyword}&filter=hum_ani.humans&filter=years.2000-2001&size=200&page=1"
# new = re.sub(r"years.\d{4}-\d{4}", "year.2010-2011", txt)
# print(new)

import pandas as pd
from Pubmed import Pubmed
from PubmedGroup import PubmedGroup

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import ElementClickInterceptedException
import re

# first = Pubmed("hyperthyroidie")
# first.RetrieveArticles()

test = PubmedGroup(["Hyperthyroidie", "Hypothyroidie", "goitre", "thyroidites"])
test.StartRetrieve()
test.JoinDataframe()

# txt = "https://pubmed.ncbi.nlm.nih.gov/?term={keyword}&filter=hum_ani.humans&filter=years.2000-2001&size=200&page=1"
# new = re.sub(r"years.\d{4}-\d{4}", "year.2010-2011", txt)
# print(new)

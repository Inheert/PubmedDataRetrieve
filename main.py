import pandas as pd
from PubMed import *

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import ElementClickInterceptedException


first = Pubmed("%28autoimmune+thyroid+disease%29+AND+%28neplasms%29")
first.RetrieveArticles()




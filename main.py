from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import os
import time

os.environ["GH_TOKEN"] = "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"


service = Service(executable_path=GeckoDriverManager().install())

directory = f"{os.path.abspath(os.curdir)}/testSave"

options = Options()
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("browser.download.dir", directory)
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")

driver = webdriver.Firefox(service=service, options=options)
driver.implicitly_wait(0.5)

driver.get("https://pubmed.ncbi.nlm.nih.gov/?term=thyroid")

button = driver.find_element(by=By.ID, value='save-results-panel-trigger')
button.click()

select = Select(driver.find_element(by=By.ID, value='save-action-selection'))
select.select_by_visible_text('All results')

select = Select(driver.find_element(by=By.ID, value='save-action-format'))
select.select_by_visible_text('PubMed')

button2 = driver.find_element(by=By.CLASS_NAME, value='action-panel-submit')
button2.click()

time.sleep(60)

driver.quit()

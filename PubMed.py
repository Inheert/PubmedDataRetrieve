from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import os
import time
from uuid import uuid4

class Pubmed:

    def __init__(self, url):
        self.url = url
        self.uid = uuid4().hex


    def _Initialize(self):
        pass

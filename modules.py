from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException
from selenium import webdriver
from selenium.webdriver.support.ui import Select

import os
import shutil
import platform
import glob
import time
from uuid import uuid4
import pandas as pd
from datetime import datetime
import re
import threading

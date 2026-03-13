import json
import time
import os

#selenium
import os.path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

#chrome options for wd
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")

#path to chromedriver
homedir = os.path.expanduser("~")

webdriver_service = Service()

#create webdriver
driver = webdriver.Chrome(service=webdriver_service,options=chrome_options)
driver.implicitly_wait(10)

driver.get("https://atlas.ai.umich.edu")
time.sleep(30) #time to get duo login

results = []
next_url = f"https://atlas.ai.umich.edu/api/courses/browse/?page=1&page_size={20000}&sort=alpha"
while next_url:
  driver.get(next_url)
  json_results = driver.find_element(By.TAG_NAME,'body').text
  j = json.loads(json_results)
  results.extend(j["results"])
  print(next_url, len(results))
  next_url = j["next"]
with open("atlas_linkscrape_results.json", 'w') as f:
  json.dump({"results":results}, f, indent = 2)
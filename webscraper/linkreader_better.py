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

driver.get("https://atlas.ai.umich.edu/accounts/login")
input("When you have signed in, press [Enter]:")
# get cookies
cookies_dict = {}
for cookie in driver.get_cookies():
    cookies_dict[cookie['name']] = cookie['value']
print("Cookies:",cookies_dict)

import requests
from bs4 import BeautifulSoup

# for starting from a specific index
import sys
start = 0
if len(sys.argv)>1:
  start = int(sys.argv[1])

file_path = "atlas_linkscrape_results.json"
with open(file_path, 'r') as json_file:
  results = json.load(json_file)["results"]

file_path = "atlas_linkread_results.json"
with open(file_path, 'r') as json_file:
  results[:start] = json.load(json_file)["results"][:start]

response = None
for key in range(start, len(results)):
  if 1:
    print(key, results[key]["course_code"])
    # build url
    results[key]["Link"] = f"https://atlas.ai.umich.edu{results[key]["url"]}"
    try:
      ok_resp = False
      status_code = 0
      while not (ok_resp or status_code == 404):
        response = requests.get(results[key]["Link"], cookies=cookies_dict)
        status_code = response.status_code
        ok_resp = response.ok
      soup = BeautifulSoup(response.text, 'html.parser')

      try:
        # get the course data
        course_data = soup.find("script", id="cached-course-data")
        script_content = course_data.string

      
        data = json.loads(script_content)
        
        # get median grade, desire, understanding, workload, expectations, interest
        # median
        try:
          results[key]["Median Grade"] = data['grades']['median_grade']
        except:
          results[key]["Median Grade"] = None

        # responses
        try:
          results[key]["Desire to Take"] = data['eval_summary']['responses']['q4']
        except:
          results[key]["Desire to Take"] = None

        try:
          results[key]["Understanding"] = data['eval_summary']['responses']['q1631']
        except:
          results[key]["Understanding"] = None

        try:
          results[key]["Workload"] = data['eval_summary']['responses']['q891']
        except:
          results[key]["Workload"] = None

        try:
          results[key]["Expectations"] = data['eval_summary']['responses']['q1632']
        except:
          results[key]["Expectations"] = None

        try:
          results[key]["Interest"] = data['eval_summary']['responses']['q1633']
        except:
          results[key]["Interest"] = None

      except:
        1
      
      try:
        # get the course data
        prereq_data = soup.find("script", id="course-props-data")
        script_content = prereq_data.string

        # course_data = driver.find_element(By.ID, "cached-course-data")
      
        # script_content = course_data.get_attribute('innerHTML')
        data = json.loads(script_content)

        # get only most recent term data
        current_term_data = max(data, key=lambda x: x["term"]["code"])

        try:
          advisory_prereq = current_term_data["advisory_prereqs"].strip()
          advisory_prereq = advisory_prereq if advisory_prereq else None
        except:
          advisory_prereq = None
        results[key]["Advisory Prerequisites"] = advisory_prereq
        try:
          prereq = current_term_data["enforced_prereqs"].strip()
          prereq = prereq if prereq else None
        except:
          prereq = None
        results[key]["Enforced Prerequisites"] = prereq
      except:
        1
    except: 
      print("Couldn't find all values for",results[key]["course_code"])
      pass
    
    sections = []
    try:
      ok_resp = False
      status_code = 0
      while not (ok_resp or status_code == 404):
        response = requests.get(f"https://atlas.ai.umich.edu/api/section-table-data/{results[key]["course_code"]}", cookies=cookies_dict)
        status_code = response.status_code
        ok_resp = response.ok
      j = response.json()

      # sort sections
      j["sections"] = sorted(j["sections"], key=lambda x: str(x["SectionNumber"]))
      for n,section in enumerate(j["sections"]):
        # check each section for section data
        # find extra data for this section
        if section["ClassTopic"]:
          section_data = {"section": str(section["SectionNumber"]), "title": str(section["ClassTopic"]), "description": None}
          matched_section_data = [i for i in j["extra_data"] if i["section"] == section["SectionNumber"]]
          if matched_section_data:
            # driver.get(f"https://atlas.ai.umich.edu/api/sections/{matched_section_data[0]["id"]}/info/")

            # description_results = driver.find_element(By.TAG_NAME,'body').text

            ok_resp = False
            status_code = 0
            while not (ok_resp or status_code == 404):
              response = requests.get(f"https://atlas.ai.umich.edu/api/sections/{matched_section_data[0]["id"]}/info/", cookies=cookies_dict)
              status_code = response.status_code
              ok_resp = response.ok
            description_results = response.json()

            description_json = json.loads(description_results)
            section_data["description"] = description_json["description"]
          
          sections.append(section_data)
    except:
      print("Couldn't find sections for",results[key]["course_code"])
    results[key]["Sections"] = sections

  # update file every so often
  if not key%25:
    with open(file_path, 'w') as json_file:
        json.dump({"results":results}, json_file,indent=2)

  # keep session alive?
  # if not key%100:
  #   driver.get(results[key]["Link"])
  #   for cookie in driver.get_cookies():
  #     cookies_dict[cookie['name']] = cookie['value']

driver.close()

with open(file_path, 'w') as json_file:
    json.dump({"results":results}, json_file,indent=2)
print("Finished adding information from links.")
print("Data was stored in",file_path)

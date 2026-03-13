import json
import time
import os
import sys

#selenium
import os.path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

letter=sys.argv[1]
print("Letter analyzed is",letter)

#read in links json
file_path = "webscraper/data/letters/atlasdict"+letter+".json"
with open(file_path, 'r') as json_file:
  results = json.load(json_file)

#chrome options for wd
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")

#path to chromedriver
homedir = os.path.expanduser("~")

# webdriver_service = Service(f"C:/Users/danie/chromedriver/stable/chromedriver.exe")
webdriver_service = Service()

#create webdriver
driver = webdriver.Chrome(service=webdriver_service,options=chrome_options)
driver.implicitly_wait(10)

driver.get("https://atlas.ai.umich.edu")
time.sleep(30) # time to get logged in with duo

i=0
for key in results:
  i+=1
  if i%100==0:
    file_path = "webscraper/data/letters/atlasdict"+letter+".json"
    with open(file_path, 'w') as json_file:
        json.dump(results, json_file,indent=2)
    print("Finished adding information from links.")
    print("Data was stored in",file_path)
  if key[0]==letter and (results[key]["Class Title"]==None or results[key]["Median Grade"]==None or results[key]["Credits"]==None or results[key]["Desire to Take"]==None or results[key]["Understanding"]==None or results[key]["Workload"]==None or results[key]["Expectations"]==None or results[key]["Increased Interest"]==None):
    print(key)
    try:
      driver.get(results[key]["Link"])
      title=driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]/h2").text
      results[key]["Class Title"]=title
      try:
        credits=float(driver.find_element(By.XPATH,'//*[@id="credits"]/p').text[9:])
      except:
        try: 
          credits = driver.find_element(By.XPATH,'//*[@id="credits"]/p').text[9:]
        except: 
          credits = None
      results[key]["Credits"]=credits
      try: 
        mediangrade=driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div/div[2]/div/p[1]/span").text
      except: 
        mediangrade=None
      results[key]["Median Grade"] = mediangrade
      try:
        desire=int(driver.find_element(By.XPATH,"/html/body/div[1]/div[4]/div[2]/div[1]/div[1]/h5").text[:-1])
      except: 
        desire = None 
      results[key]["Desire to Take"] = desire
      try:
        understanding=int(driver.find_element(By.XPATH,"/html/body/div[1]/div[4]/div[2]/div[2]/div[1]/h5").text[:-1])
      except: 
        understanding=None
      results[key]["Understanding"] = understanding
      try:
        workload=int(driver.find_element(By.XPATH,"/html/body/div[1]/div[4]/div[2]/div[3]/div[1]/h5").text[:-1])
      except: 
        workload=None
      results[key]["Workload"] = workload
      try:
        expectations=int(driver.find_element(By.XPATH,"/html/body/div[1]/div[4]/div[2]/div[4]/div[1]/h5").text[:-1])
      except: 
        expectations=None
      results[key]["Expectations"] = expectations
      try:
        interest=int(driver.find_element(By.XPATH,"/html/body/div[1]/div[4]/div[2]/div[5]/div[1]/h5").text[:-1])
      except:
        interest = None
      results[key]["Increased Interest"] = interest
      try:
          advisory_prereq_div = driver.find_element(By.CSS_SELECTOR, "div.prereq.advisory")
          advisory_prereq = advisory_prereq_div.find_element(By.CSS_SELECTOR, "p.text-small").text
      except:
        advisory_prereq = None
      results[key]["Advisory Prerequisites"] = advisory_prereq
      try:
        prereq_div = driver.find_element(By.CSS_SELECTOR, "div.prereq:not(.advisory)")
        prereq = prereq_div.find_element(By.CSS_SELECTOR, "p.text-small").text
      except:
        prereq = None
      results[key]["Enforced Prerequisites"] = prereq
    except: 
      print("Couldn't find all values for",key)
      pass
    
    # grab section info
    try:
      rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
      sections = []
      for row in rows:
          try:
              btn = row.find_element(By.CSS_SELECTOR, "button.expand-btn")
              btn.click()

              section_name = None
              section_title = None

              try:
                section_name = row.find_element(By.CSS_SELECTOR, "div.section-name").text.split("\n")[0].strip()
              except:
                section_name = None
              try:
                section_title = row.find_element(By.CSS_SELECTOR, "span.course-title").text.strip()
              except:
                section_title = None

              description = None
              try:
                  next_row = driver.execute_script("return arguments[0].nextElementSibling;", row)
                  desc_cell = next_row.find_element(By.CSS_SELECTOR, "td.section-description")
                  description = desc_cell.text.strip()
              except:
                  description = None

              # only add if section title exists - will not add things like unnamed lecture/discussion sections
              if section_title:
                sections.append({"section": section_name, "title": section_title, "description": description})
          except:
            pass
      results[key]["Sections"] = sections
    except:
      pass 

driver.close()

file_path = "webscraper/data/letters/atlasdict"+letter+".json"
with open(file_path, 'w') as json_file:
    json.dump(results, json_file,indent=2)
print("Finished adding information from links.")
print("Data was stored in",file_path)

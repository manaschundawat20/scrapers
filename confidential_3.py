import sys
import time
import os
import csv
import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import bs4 as bs
from datetime import datetime, timedelta
import math
import pandas as pd
import re
import shutil
import requests
from bs4 import BeautifulSoup


class Spud:
    def __init__(self) -> None:

        self.driver = None
        self.file_dir = "/var/www/html/py/ob_occ/output/spudddd/"
        self.process_id = []
        self.item = []  # Initialize the item attribute
        self.init_driver()

    def init_driver(self):
        # Initialize Chrome webdriver
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument('--no-sandbox')
        chromeOptions.add_argument('--disable-gpu')
        chromeOptions.add_argument("--start-maximized")
        chromeOptions.add_argument('--disable-dev-shm-usage')
        chromeOptions.add_argument('--allow-running-insecure-content')
        chromeOptions.add_argument('--ignore-certificate-errors')
        chromeOptions.add_argument('--allow-insecure-localhost')
        # Preferences for Chrome options
        prefs = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
                 "download.default_directory": str(self.file_dir), "prompt_for_download": False, "plugins.always_open_pdf_externally": True}
        chromeOptions.add_experimental_option("prefs", prefs)
        chromeOptions.ignore_local_proxy_environment_variables()
        chrome_kwargs = {'options': chromeOptions, 'keep_alive': False}
        driver = webdriver.Chrome(**chrome_kwargs)
        self.driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=chromeOptions)

    def selenium_data(self):
        print("start selenium function here ")
        url = 'https://public.occ.ok.gov/OGCDWellRecords/SearchService.aspx/GetSearchListing'

        payload = {
            "repoName": "OCC",
            "searchSyn": "({LF:templateid=55} & ({LF:LOOKIN=\"\\OGCD\\Well Records\"}) & {[]:[Form Number]=\"1001A\"} & {[]:[Scan Date]>=\"02/01/2024\", [Scan Date]<=\"02/05/2024\"})",
            "searchUuid": "d4e53954-539e-44f8-a527-236cfa9a0a9f",
            "sortColumn": "",
            "startIdx": 0,
            "endIdx": 100,
            "getNewListing": 'false',
            "sortOrder": 2,
            "displayInGridView": 'true'
        }

        print("payload here")
        print(payload)
        s = requests.Session()
        response = s.post(url, json=payload)
        print(response.status_code)
        startindex = 100
        page_offset = 100
        total_page = 4

        if response.status_code == 200:
            # data = response.text

            print(response)
            # print(response.text)
            result = response.json()
            print("result")
            # print(result)
            total_count = result["data"]["hitCount"]
            print("total count")
            print(total_count)
            res1 = result["data"]["results"]
            print(res1)
            actual_result = len(res1)
            page_count = 1
            entry_ids = []

            if total_count > actual_result:
                page_count = math.ceil(total_count / actual_result)

            for res in res1:
                print(res)
                print(res["name"])
                print("new")
                print(res["entryId"])
                entry_ids.append(res["entryId"])  # Append entryId to list

                print("new1")
                print(res["data"])
                file_name = res["data"][0]
                print(file_name)

            return entry_ids  # Return list of entryIds

    def download_files(self):
        entry_ids = self.selenium_data()
        print("List of entryIds:", entry_ids)
        time.sleep(1)
        # Loop through each entry ID, extract data, and download files
        for entry_id in entry_ids:
            self.extract_data(entry_id)
            time.sleep(3)

    def wait_for_downloads(self, path_to_downloads):
        seconds = 0
        dl_wait = True
        while dl_wait and seconds < 1000:
            time.sleep(1)
            dl_wait = False
            for fname in os.listdir(path_to_downloads):
                if fname.endswith('.crdownload'):
                    dl_wait = True
            seconds += 1
        print(f"Downloads completed in {seconds} seconds.")

    def rename_files(self, file_dir):
        for file_path in os.listdir(file_dir):
            if os.path.isfile(os.path.join(file_dir, file_path)):
                new_file = file_path.replace(" ", "-")
                new_file = new_file.replace("\xa0", "-")
                new_file = new_file.replace(
                    "!@#$%^&*() []{};:,/<>?\\|`~-=_+", "-")
                new_file = new_file.replace("[", "-").replace("]", "-")
                new_file = re.sub(
                    "[!*#$@&_%,(){};:<>?\\|`~=+ ]", "-", new_file)

                new_file = new_file.replace("----", "-").lower()
                new_file = new_file.replace("---", "-")
                new_file = new_file.replace("--", "-")
                new_file = new_file.replace("--", "-")

                src_file = os.path.join(file_dir, file_path)
                dest_file = os.path.join(file_dir, new_file)
                os.rename(src_file, dest_file)

    def main(self):
        try:
            # Step 1: Get entry IDs using Selenium
            entry_ids = Spud.selenium_data(self)
            print("List of entryIds:", entry_ids)
            time.sleep(1)
            # Step 2: Loop through each entry ID, extract data, and append to self.item
            # entry_ids = ['14333146','14322842']
            for entry_id in entry_ids:
                item_data = self.extract_data(entry_id)
                self.item.append(item_data)
                time.sleep(3)
            # Step 3: Wait for downloads to complete
            download_path = "/var/www/html/py/ob_occ/output/spudddd/"
            self.wait_for_downloads(download_path)
            print("Downloads completed.")
            time.sleep(5)

            # Step 4: Rename downloaded files
            self.rename_files(download_path)
            print("File renaming completed.")

            # Step 5: Save extracted data to a CSV file
            csv_file_path = '/var/www/html/py/ob_occ/output/spudddd/spud_scraped_data.csv'
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.DictWriter(
                    csv_file, fieldnames=self.item[0].keys())
                csv_writer.writeheader()
                csv_writer.writerows(self.item)
            print(f"All Scraped data saved to {csv_file_path}.")

        except Exception as e:
            print(f"An error occurred: {e}")

        print("Scraping completed.")

    def extract_data(self, entry_id):
        print("we are in the extract data page")
        spud_dict = {
            "record-id": "",
            "resource-name": "",
            "state": "OK",
            "file-name": "",
            "url": "",
            "effective-date": "",
            "scan-date": "",
            "api": "",
            "well-name": "",
            "occ-otc-number": "",
            "permit-number": "",
            "permit-date": "",
            "date-spud": "",
            "date-reentry": "",
            "operator": "",
            "lease-name": "",
            "section": "",
            "township": "",
            "range": "",
            "description": "",
            "cementer-company-name": "",
            "comment": ""
        }

        # for entry_id in entry_ids:
        print("detail url here")
        detail_url = "https://public.occ.ok.gov/WebLink/DocView.aspx?id=" + \
            str(entry_id)+"&dbid=0&repo=OCC"
        self.driver.get(detail_url)

        print("start finding")
        table_id = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, 'metadataTable')))
        time.sleep(3)
        rows = table_id.find_elements(By.TAG_NAME, "tr")
        dict = {}
        for row in rows:
            time.sleep(4)

            col = row.find_elements(By.TAG_NAME, "td")
            if len(col) > 1:
                col1 = row.find_elements(By.TAG_NAME, "td")[0]
                if col1.text != "":
                    col2 = row.find_elements(By.TAG_NAME, "td")[1]
                    dict[col1.text] = col2.text

            time.sleep(1)

        file_name = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'noBreadcrumbTitle')))
        file_name = file_name.text
        # Replace unwanted characters in the file name
        file_name = file_name.replace(" ", "-")
        file_name = file_name.replace("\xa0", "-")
        file_name = file_name.replace("!@#$%^&*() []{};:,/<>?\\|`~-=_+", "-")
        file_name = file_name.replace("[", "-").replace("]", "-")
        file_name = re.sub("[!*#$@&_%,(){};:<>?\\|`~=+ ]", "-", file_name)

        file_name = file_name.replace("----", "-").lower()
        file_name = file_name.replace("---", "-")
        file_name = file_name.replace("--", "-")
        file_name = file_name.replace("--", "-")

        print("Modified file name:", file_name)

        print(file_name)

        get_url = self.driver.current_url
        print(get_url)
        spud_dict["file-name"] = str(file_name) + '.pdf'
        spud_dict["url"] = get_url

        api = ""
        if "API Number" in dict:
            api = dict["API Number"]
            data_str = api[0]
            print(data_str)
        spud_dict["api"] = api

        well_name = ""
        if "Well Name" in dict:
            well_name = dict["Well Name"]
            dta_str = well_name[0]
            print(dta_str)
        spud_dict["well-name"] = well_name

        effective_date = ""
        if "Effective Date" in dict:
            effective_date = dict["Effective Date"].split(' ')
            date_string = effective_date[0]
            # Convert date string to YMD format
            print(date_string)
            effective_date = datetime.strptime(date_string, '%m/%d/%Y')
            effective_date = effective_date.strftime('%Y-%m-%d')
            print(effective_date)
            print(date_string)
        spud_dict["effective-date"] = effective_date

        scan_date = ""
        if "Scan Date" in dict:
            scan_date = dict["Scan Date"].split(' ')
            d_str = scan_date[0]
            # Convert date string to YMD format
            print(d_str)
            scan_date = datetime.strptime(d_str, '%m/%d/%Y')
            scan_date = scan_date.strftime('%Y-%m-%d')
            print("scan date here ")
            print(d_str)
        spud_dict["scan-date"] = scan_date

        location = ""
        if "Location" in dict:
            location = dict["Location"]
            print("Original Location:", location)

            # Extracting values based on positions
            section = location[:2]
            township = location[2:5]
            range_val = location[5:8]
            description_part = location[8:].strip()
            description_part = description_part[2:]

            # Assigning values to the dictionary
            spud_dict["section"] = section
            spud_dict["township"] = township
            spud_dict["range"] = range_val
            spud_dict["description"] = description_part

            # Printing the extracted values
            print("Section:", section)
            print("Township:", township)
            print("Range:", range_val)
            print("Full Description:", description_part)

            print("we are now in the download fucntion")
            time.sleep(6)
            download_item = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="STR_DOWNLOAD_PDF"]')))
            download_item.click()
            print("done here come at dwnld")

            download_print = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="dialogButtons"]/button[1]')))
            download_print.click()
            print("complete dwnld")

            # time.sleep(6)

            print("printing dctionary here ")
            print(spud_dict)
            print("return dictionary ")
            return spud_dict

        print("complete till dictioanry work")
        print("All done !!! ")


if __name__ == "__main__":
    capture = Spud()
    capture.main()

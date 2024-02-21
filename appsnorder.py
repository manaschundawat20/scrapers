import sys
import time
import os
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

urllist = []  # Initialize an empty list to store URLs
now = datetime.now()  # Get the current date and time
# print("now =", now)  # This line is commented out and won't be executed
current_file_name = now.strftime("%d%b")  # Format the current date as "ddMon"


class capture:
    # Initialize a variable to store the driver object
    driver = None
    urls = []  # Initialize an empty list to store URLs
    download_file = {}  # Initialize an empty dictionary to store downloaded files
    file_name = []  # Initialize an empty list to store file names
    missing_url = []  # Initialize an empty list to store missing URLs
    order_multiple_file = []
    items = []  # Initialize an empty list to store items
    # Set the directory path for downloaded files
    file_dir = "/var/www/html/py/ob_occ/output/appsnorder"
    csv_file = "/var/www/html/py/ob_occ/output/appsnorder/" + \
        str(current_file_name).lower() + \
        ".csv"  # Set the path for the CSV file

    def __init__(self) -> None:
        # Call the init_driver method to initialize the driver object
        self.init_driver()

    def init_driver(self):

        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument('--no-sandbox')
        chromeOptions.add_argument('--disable-gpu')
        chromeOptions.add_argument("--start-maximized")

        # chromeOptions.add_argument('--headless')
        chromeOptions.add_argument('--disable-dev-shm-usage')
        chromeOptions.add_argument('--allow-running-insecure-content')
        chromeOptions.add_argument('--ignore-certificate-errors')
        chromeOptions.add_argument('--allow-insecure-localhost')
        # chromeOptions.add_argument("download.default_directory="+str(self.file_dir))
        # prefs = {"download.default_directory" : str(self.file_dir),"prompt_for_download": False,"plugins.always_open_pdf_externally": True }
        # chromeOptions.add_experimental_option("prefs",prefs)
        chromeOptions.add_argument(
            "download.default_directory="+str(self.file_dir))

        # Preferences for Chrome options
        prefs = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
                 "download.default_directory": str(self.file_dir), "prompt_for_download": False, "plugins.always_open_pdf_externally": True}
        chromeOptions.add_experimental_option("prefs", prefs)
        chromeOptions.ignore_local_proxy_environment_variables()
        chrome_kwargs = {'options': chromeOptions, 'keep_alive': False}
        driver = webdriver.Chrome(**chrome_kwargs)

        # Initialize the Chrome driver
        self.driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=chromeOptions)

    def open_page(self, url):
        # open the specific url in the driver
        self.driver.get(url)

    def set_filter(self, select_order):
        """
        Set filter 
        """
        now = datetime.now()
        # print("now =", now)

        # dd/mm/YY H:M:S
        # Get the current date and time
        current_date = now.strftime("%m/%d/%Y")
        # Format the current date as "dd/mm/YYYY"

        # Get the datetime of yesterday
        yesterday_datetime = datetime.now() - timedelta(days=1)  # for 2 day day=2

        # Format the previous date as "dd/mm/YYYY"
        previous_date = yesterday_datetime.strftime('%m/%d/%Y')

        # Assign the driver object to a local variable
        driver = self.driver

        driver.implicitly_wait(5)
        # Select the option with visible text "CD-Conservation Docket"
        sel1 = Select(driver.find_element(
            By.XPATH, "//select[@id='ImagedCaseDocumentsfiledafter3212022_Input2']"))
        sel1.select_by_visible_text("CD-Conservation Docket")
        sel = Select(driver.find_element(
            By.XPATH, "//select[@id='ImagedCaseDocumentsfiledafter3212022_Input3']"))

        # Select the option with the specified visible text
        sel.select_by_visible_text(select_order)
        start_date = driver.find_element(
            By.ID, "ImagedCaseDocumentsfiledafter3212022_Input6")
        # Clear the input field
        start_date.clear()

        # Enter the previous date into the input field
        start_date.send_keys(previous_date)
        end_date = driver.find_element(
            By.ID, "ImagedCaseDocumentsfiledafter3212022_Input6_end")

        # Clear the input field
        end_date.clear()

        # Enter the current date into the input field
        end_date.send_keys(current_date)

        # Click on the element with the specified class name
        driver.find_element(By.CLASS_NAME, "CustomSearchSubmitButton").click()

    def read_result(self):
        # Pause the execution for 2 seconds
        time.sleep(2)
        # Initialize a variable to store the total number of pages
        tot_pages = 0

        try:
            pages = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="resultText"]/span[2]'))
            )
            # Wait for the element with the specified XPath to be present
            # Find the element with the specified XPath
            pages = self.driver.find_element(
                By.XPATH, '//*[@id="resultText"]/span[2]')

            # Get the text content of the element
            pages_txt = pages.text

            # Print the text content of the element
            print(pages_txt)

            # Split the text content by the word "of"
            pages_tot = pages_txt.split("of")
            # Get the range of pages

            pages_ranges = pages_tot[0].strip()

            # Get the offset value
            pages_offset = int(pages_tot[1].strip())
        except:
            # Set the total number of pages to 1
            tot_pages = 1
            pages_offset = 1

        if pages_offset > 0:
            if tot_pages != 1:
                page_limit = pages_ranges.split("-")
                plimit = int(page_limit[1].strip())
                total_pages = pages_offset/plimit

                tot_pages = math.ceil(total_pages)
            # tot_pages = 1
            print(tot_pages)

            for page_num in range(tot_pages):
                # Extract the data from the current page
                page_output = self.extract_page_data()
                self.driver.implicitly_wait(4)
                if tot_pages > 1:
                    next_page = self.driver.find_element(
                        By.CLASS_NAME, 'NextPageLink').click()
                # todo remove break
                # break
            # Add the data to the final_out list as a dictionary with the page number as the key
                # final_out.append({
                #     page_num: page_output
                # })
            # Locate the "Next" button on the webpage and click it to navigate to the next page

            print(self.urls)
            print(len(self.urls))

    def extract_page_data(self):
        driver = self.driver
        parent = driver.find_elements(
            By.XPATH, '//*[@id="ResultsDivContainer"]/div[2]')
        elements = parent[0].find_elements(
            By.XPATH, "//*[@class='ResultItem']")
        urls = []
        current_handle = driver.window_handles[0]
        for element in elements:
            # print(element.text)
            a = element.find_element(By.CLASS_NAME, "DocumentBrowserNameImage")
            span = element.find_element(By.XPATH, "//span")
            print(span.text)
            a.click()

            # window_handles[1] is a second window

            driver.switch_to.window(driver.window_handles[1])
            print(driver.current_url)
            self.urls.append(driver.current_url)
            driver.close()
            driver.switch_to.window(current_handle)
            print(driver.current_url)

            # prints the title of the second window
            print("Second window title = " + driver.title)

            # window_handles[0] is a first window
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)
            print("resume after 2")
            print("first window title = " + driver.title)

            # prints windows id
            print(driver.window_handles)

            print("waiting for 2 secs")

            time.sleep(1)
            # break
            # element.click()
        print(self.urls)
        time.sleep(1)
        print("wait here")

    def process_urls(self):
        self.init_driver()
        yesterday_datetime = datetime.now() - timedelta(days=1)
        previous_date = yesterday_datetime.strftime('%d/%m/%Y')
        scan_date = yesterday_datetime.strftime('%Y-%m-%d')

        alldict = []
        urls = self.urls
        self.missing_url = []

        print("Total url:")
        print(len(urls))
        for link in urls:
            time.sleep(5)
            print(link)

            self.driver.get(link)
            get_url = self.driver.current_url
            self.driver.implicitly_wait(2)
            time.sleep(1)
            element_not_found = 0
            try:
                file_name = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'noBreadcrumbTitle')))
            except:
                print("element not found")
                if get_url not in self.missing_url:
                    self.missing_url.append(get_url)
                element_not_found = 1
            if element_not_found == 1:
                continue
            file_name = file_name.text
            print(file_name)
            # file_name = file_name.replace(" ","")
            self.file_name.append(file_name)
            # act_file = re.sub("[!@#$%^&*()[] {};:,./<>?\|`,~-=_+]", "-", file_name)
            # act_file = re.sub("[!@#$%^&*()[]{};:,./<>?\|`,~-=_+]", "-", file_name)
            act_file = file_name.replace("!@#$%^&*() []{};:,/<>?\|`~-=_+", "-")
            act_file = file_name.replace("[", "-").replace("]", "-")
            act_file = re.sub("[!*#$@&_%,(){};:<>?\|`~=+ ]", "-", act_file)
            act_file = act_file.replace("----", "-").lower()
            act_file = act_file.replace("---", "-")

            act_file = act_file.replace("--", "-")
            act_file = act_file.replace("--", "-")
            print(file_name)
            self.download_file[file_name] = act_file
            file_name = act_file
            print(file_name)
            print(self.download_file)
            # file_name = file_name.replace("_","-")
            res = re.findall('([a-zA-Z ]*)\d*.*', file_name)

    # printing result
            print("Extracted String : " + str(res[0]))
            case_type = res[0]
            # if case_type == "CD":
            if True:
                get_url = self.driver.current_url
                record_id = get_url.split("?id=")
                record_id = record_id[1].split("&dbid")
                record_id = record_id[0]

                time.sleep(1)

                osberg_dict = {"record-id": "", "resource-name": "", "file-name": "", "url": "", "state": "OK", "cause-num": "", "order-num": "", "docket-code": "APPLIC", "case-type": "CD", "effective-date": "", "scan-date": "", "applicant": "", "type": "", "section": "", "township": "", "range": "", "county": "", "description": "", "lot": "", "primary": "", "court": "", "hearing": "", "label": "", "horizontal-well": "", "contact": "", "cont-tel": "", "number-of-respondents": "", "option-1": "", "option-2": "", "option-3": "", "option-4": "", "option-5": "", "more-info": "", "dry": "", "completed": "", "comment": "", "related-well": "", "existing-well": "", "distance-well": "", "eur": "", "eur-measurement": "", "existing-well-recovery": "", "additional-well-numbers": "",
                               "commencement-of-operations": "", "allowable": "", "allowable-measurement": "", "allowable-comment": "", "surface-location": "", "terminus-location": "", "terminus-depth": "", "first-perforation-location": "", "first-perforation-depth": "", "last-perforation-location": "", "last-perforation-depth": "", "spacing-exception-order-number": "", "companion-causes": "", "point-of-entry-location": "", "point-of-entry-depth": "", "completion-interval-location": "", "completion-interval-depth": "", "point-of-exit-location": "", "point-of-exit-depth": "", "tolerance-feet": "", "current-operator": "", "classification": "", "otc-prod-unit": "", "occ-number-current-operator": "", "occ-number-new-operator": "", "api": "", "allocations": ""}

                dict = {"record_id": record_id,
                        "file_name": file_name, "url": get_url}
                # osberg_dict["record-id"] = record_id
                osberg_dict["file-name"] = file_name
                osberg_dict["url"] = get_url
                # table_id = self.driver.find_element(By.ID, 'metadataTable')
                table_id = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, 'metadataTable')))

                rows = table_id.find_elements(By.TAG_NAME, "tr")
                element_not_found = 0
                for row in rows:
                    time.sleep(1)
                    # Get the columns (all the column 2)
                    #
                    try:
                        col = row.find_elements(By.TAG_NAME, "td")

                        if len(col) > 1:
                            col1 = row.find_elements(By.TAG_NAME, "td")[0]
                            if col1.text != "":

                                col2 = row.find_elements(By.TAG_NAME, "td")[1]

                                dict[col1.text] = col2.text
                    except:
                        print("Element not found")
                        element_not_found = 1
                        if get_url not in self.missing_url:
                            self.missing_url.append(get_url)

                    # print(col.text) #prints text from the element
                # if
                if element_not_found == 1:
                    continue
                print(dict)
                print(dict["ECF Case Number"])

                osberg_dict["cause-num"] = dict["ECF Case Number"].replace(
                    "-", "")
                osberg_dict["cause-num"] = dict["ECF Case Number"].replace(
                    "-", "")
                order_num = ""
                if "ECF Order Number" in dict:
                    osberg_dict["order-num"] = dict["ECF Order Number"]
                    order_num = dict["ECF Order Number"]
                file_list_array = []
                if case_type != "cd":
                    order_case = osberg_dict["cause-num"]
                    order_list = order_case.split('\n')
                    print(order_list)
                    if len(order_list) > 1:
                        self.order_multiple_file.append(file_name+".pdf")
                        for val in order_list:
                            file_list_array.append(val)
                    else:
                        file_name = osberg_dict["cause-num"] + \
                            "-"+file_name+".pdf"
                        file_name = file_name
                        print(file_name)
                        osberg_dict["file-name"] = file_name
                    osberg_dict["docket-code"] = "ORDER"

                modified_date = ""
                effective_date = ""
                if "Modified" in dict:
                    modified_date = dict["Modified"].split(" ")
                    # print(modified_date)
                    date_string = modified_date[0]
                    print(date_string)
                    try:
                        date_object = datetime.strptime(
                            date_string, "%m/%d/%Y")
                    except:
                        print("missing date format")
                    effective_date = date_object.strftime("%Y-%m-%d")
                    # date_array = modified_date[0].split("/")
                    osberg_dict["effective-date"] = effective_date
                    print("Effective date-")
                    print(osberg_dict["effective-date"])
                    # effective_date = date_array[2]+"-"+date_array[0]+"-"+date_array[1]

                # modified_date = dict["Modified"].split(" ")
                # osberg_dict["effective-date"] = modified_date[0]
                osberg_dict["scan-date"] = scan_date
                time.sleep(1)
                if case_type == "cd":
                    download_item = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.ID, 'STR_DOWNLOAD')))
                    download_item.click()
                else:

                    download_item = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="STR_DOWNLOAD_PDF"]')))
                    download_item.click()
                    download_print = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="dialogButtons"]/button[1]')))
                    download_print.click()
                    # time.sleep(4)
                    # get_data = self.driver.page_source
                    # print(get_data)

                    # download_cl = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="icon"]')))
                    # download_cl.click()

                    # //*[@id="dialogButtons"]

                # self.driver.find_element(By.ID,"STR_DOWNLOAD").click()
                if len(file_list_array) > 1:
                    for file_val in file_list_array:
                        print(file_val)
                        osberg_dict_order = {"record-id": "", "resource-name": "", "file-name": "", "url": "", "state": "OK", "cause-num": "", "order-num": "", "docket-code": "APPLIC", "case-type": "CD", "effective-date": "", "scan-date": "", "applicant": "", "type": "", "section": "", "township": "", "range": "", "county": "", "description": "", "lot": "", "primary": "", "court": "", "hearing": "", "label": "", "horizontal-well": "", "contact": "", "cont-tel": "", "number-of-respondents": "", "option-1": "", "option-2": "", "option-3": "", "option-4": "", "option-5": "", "more-info": "", "dry": "", "completed": "", "comment": "", "related-well": "", "existing-well": "", "distance-well": "", "eur": "", "eur-measurement": "", "existing-well-recovery": "",
                                             "additional-well-numbers": "", "commencement-of-operations": "", "allowable": "", "allowable-measurement": "", "allowable-comment": "", "surface-location": "", "terminus-location": "", "terminus-depth": "", "first-perforation-location": "", "first-perforation-depth": "", "last-perforation-location": "", "last-perforation-depth": "", "spacing-exception-order-number": "", "companion-causes": "", "point-of-entry-location": "", "point-of-entry-depth": "", "completion-interval-location": "", "completion-interval-depth": "", "point-of-exit-location": "", "point-of-exit-depth": "", "tolerance-feet": "", "current-operator": "", "classification": "", "otc-prod-unit": "", "occ-number-current-operator": "", "occ-number-new-operator": "", "api": "", "allocations": ""}
                        dict_val = osberg_dict
                        file_name = file_val+"-"+act_file+".pdf"
                        osberg_dict_order["file-name"] = file_name
                        osberg_dict_order["cause-num"] = file_val
                        osberg_dict_order["effective-date"] = effective_date
                        osberg_dict_order["scan-date"] = scan_date
                        osberg_dict_order["order-num"] = order_num
                        osberg_dict_order["url"] = get_url
                        osberg_dict_order["docket-code"] = "ORDER"
                        print(dict_val)
                        osberg_dict["file-name"] = file_name
                        osberg_dict["cause-num"] = file_val
                        alldict.append(osberg_dict_order)
                        self.items.append(osberg_dict_order)
                else:
                    print(osberg_dict)
                    alldict.append(osberg_dict)
                    self.items.append(osberg_dict)
                time.sleep(1)
                self.download_wait(self.file_dir)
                print(self.items)
                # if case_type !="cd":
                #     print(order_list)

                # else:

                #     alldict.append(osberg_dict)
        if len(self.items) > 0 and len(self.missing_url) == 0:
            df = pd.DataFrame(self.items)
            # df.replace("\n", )
            # df.drop(columns = df.columns[0], axis = 1, inplace= True)

            now = datetime.now()
            current_date = now.strftime("%d-%m-%y")
            df.to_csv(self.csv_file, index=False)
            print("missing url start")
            print(self.missing_url)
            print("missing url end")
        elif len(self.urls) > 0:
            self.urls = self.missing_url
            print("missing url start")
            print(self.missing_url)
            print("missing url end")
            self.process_urls()

    def download_wait(self, path_to_downloads):
        seconds = 0
        dl_wait = True
        while dl_wait and seconds < 800:
            time.sleep(1)
            dl_wait = False
            for fname in os.listdir(path_to_downloads):
                if fname.endswith('.crdownload'):
                    dl_wait = True
            seconds += 1
        return seconds

    def rename_file(self):
        files = self.download_file
        file_dir = self.file_dir
        for file_path in os.listdir(file_dir):
            # check if current file_path is a file
            if os.path.isfile(os.path.join(file_dir, file_path)):

                print(file_path)
                new_file = file_path.replace(" ", "-")
                new_file = new_file.replace("\xa0", "-")
                new_file = new_file.replace(
                    "!@#$%^&*() []{};:,/<>?\|`~-=_+", "-")
                new_file = new_file.replace("[", "-").replace("]", "-")
                new_file = re.sub("[!*#$@&_%,(){};:<>?\|`~=+ ]", "-", new_file)

                print(new_file)
                new_file = new_file.replace("----", "-").lower()
                new_file = new_file.replace("---", "-")

                new_file = new_file.replace("--", "-")
                new_file = new_file.replace("--", "-")

                print(file_path)
                print(new_file)
                src_file = file_dir+"/"+file_path
                dest_file = file_dir+"/"+new_file
                os.rename(src_file, dest_file)
        print(self.csv_file)
        df = pd.read_csv(self.csv_file)
        for index, row in df.iterrows():
            # print(row)
            if row['file-name'] != "" and row['file-name'] != None and row['docket-code'] == 'ORDER':
                file_name = row['file-name']
                # print(file_name)
                get_file = file_name.split("-")
                # print(get_file[1])
                get_src_file = get_file[1]
                print(get_src_file)
                get_dest_file = file_name
                print(get_dest_file)
                src_file = file_dir+"/"+get_src_file
                dest_file = file_dir+"/"+get_dest_file

                os.rename(src_file, dest_file)
                if get_src_file in self.order_multiple_file:
                    shutil.copy(dest_file, src_file)
                # shutil.copy(dest_file, src_file)
        time.sleep(1)
        if len(self.order_multiple_file) > 0:
            for multiple_file in self.order_multiple_file:
                remove_file = file_dir+"/"+multiple_file

                if os.path.isfile(remove_file):
                    os.remove(remove_file)

    def run(self):
        url = "https://public.occ.ok.gov/WebLink/CustomSearch.aspx?SearchName=ImagedCaseDocumentsfiledafter3212022&dbid=0&repo=OCC"
        self.open_page(url=url)
        # orderlist = ['Application','Application - Amended ','Application/Motion for Emergency Relief','Interim Order','Emergency Order','Final Order','Dismissal Order','Nunc Pro Tunc','Other Motion Order','Order Dismissing Application or Complaint Upon Motion of the Applicant (DMOA)']
        # orderlist = ['Application','Application - Amended ','Application/Motion for Emergency Relief']

        orderlist = ['Interim Order', 'Emergency Order', 'Final Order', 'Dismissal Order', 'Nunc Pro Tunc',
                     'Other Motion Order', 'Order Dismissing Application or Complaint Upon Motion of the Applicant (DMOA)']
        # orderlist = ['Application/Motion for Emergency Relief']
        # orderlist = ['Dismissal Order','Nunc Pro Tunc','Other Motion Order','Order Dismissing Application or Complaint Upon Motion of the Applicant (DMOA)']
        for order_item in orderlist:

            self.set_filter(order_item)

        # #read listing
            self.read_result()
            time.sleep(1)
            print("new")
        self.driver.close()
        time.sleep(1)
        # self.urls = ['https://public.occ.ok.gov/WebLink/DocView.aspx?id=14272588&dbid=0&repo=OCC&searchid=bb50b837-9844-4814-8cf8-25588ec4c4b3']
        # self.urls =['https://public.occ.ok.gov/WebLink/DocView.aspx?id=14249649&dbid=0&repo=OCC&searchid=510a43d8-408c-4c35-a923-9b4853da0aa3','https://public.occ.ok.gov/WebLink/DocView.aspx?id=14249646&dbid=0&repo=OCC&searchid=510a43d8-408c-4c35-a923-9b4853da0aa3']
        # self.urls = ['https://public.occ.ok.gov/WebLink/DocView.aspx?id=14269140&dbid=0&repo=OCC&searchid=774b49d0-e4f4-4bf6-809f-83ce67c48009']
        self.process_urls()
        time.sleep(15)
        self.driver.close()
        time.sleep(2)
        self.rename_file()

        print("all done")
        # self.driver.close()
        # sys.exit(1)


if __name__ == "__main__":
    obj_capture = capture()
    obj_capture.run()

import json
import sys
import time
import os
import selenium
import urllib
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException, TimeoutException, NoSuchElementException
from datetime import datetime, timedelta
from selenium.webdriver.common.alert import Alert


def create_folder_with_current_date(base_folder):

    try:
        current_date = datetime.now().strftime("%Y/%m_%d")
        folder_name = f"{current_date}"
        folder_path = os.path.join(base_folder, folder_name)

    # Check if the folder already exists
        if not os.path.exists(folder_path):
            # If not, create the folder
            os.makedirs(folder_path)
            print(f"Folder created at: {folder_path}")
        else:
            print(f"Folder already exists at: {folder_path}")

    # Create file directory within the folder
        file_dir = os.path.join(base_folder, current_date)
        print(f"File directory: {file_dir}")
        return file_dir

    except Exception as e:
        print(f"Exception occured in create_folder_with_current_date: {e}")

# Define a class Capture


class Capture:
    # class variables
    driver = None
    file_dir = ""

    process_id = []
    missing_id = []

    json_item = []

    # Initialize the class and set webdriver with specified options

    def __init__(self) -> None:
        self.init_driver()

    # Set Chrome Webdriver

    def init_driver(self):
        base_folder = "/var/www/html/py/ob_occ/output/caddocounty/land/"
        self.file_dir = create_folder_with_current_date(base_folder)
        # print(self.file_dir)
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument('--no-sandbox')
        chromeOptions.add_argument('--disable-gpu')
        chromeOptions.add_argument("--start-maximized")
        chromeOptions.add_argument('--disable-dev-shm-usage')
        chromeOptions.add_argument('--allow-running-insecure-content')
        chromeOptions.add_argument('--ignore-certificate-errors')
        chromeOptions.add_argument('--allow-insecure-localhost')
        # chromeOptions.add_argument('--headless')
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

    # Click initial button and open first url of webpage
    def click_initial_button(self):
        try:
            self.driver.get(
                'https://caddook.avenuinsights.com/Home/index.html')

            initial_button = self.driver.find_element(
                By.XPATH, '//*[@id="btnPublic"]')
            initial_button.click()
            time.sleep(1)
            self.driver.quit()

        except Exception as e:
            print(f"Exception occurred in click_initial_button: {e}")

    # Login to the web page with username and password
    def login(self, username, password):

        try:
            self.driver.get(
                'https://caddook.avenuinsights.com/Public/CaddoOK/Account/Login')
            username_field = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="Email"]')))
            password_field = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="Password"]')))
            username_field.clear()

            username_field.send_keys(username)  # send keys to fields
            username_field.send_keys(Keys.ENTER)
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(2)

            login_button = self.driver.find_element(By.ID, 'LoginBtn')
            login_button.click()  # click on login button
            time.sleep(5)

        except Exception as e:
            print(f"Exception occurred in login: {e}")

    # Fetch data using Selenium
    def selenium_data(self):

        try:
            now = datetime.now()
            end_date = now.strftime("%m/%d/%Y")
            # (Current date - 2 days ) # do it days=3
            start_date = datetime.now() - timedelta(days=2)
            start_date = start_date.strftime('%m/%d/%Y')

            url = "https://caddook.avenuinsights.com/Public/caddook/InstrumentGrid/Search?IndexMultiSelect=1&IndexMultiSelect=3&IndexMultiSelect=6&SearchCriteria=5&SearchType=S&value=&Name_input=&Name=&kindValue=&act=&Subdivision_input=&Subdivision=&Condos_input=&Condos=&Township_input=&Township=&CaseNumber=&StartDate="+urllib.parse.quote(str(start_date))+"&EndDate="+urllib.parse.quote(str(
                end_date))+"&Volume=&Page=&Phase=&LowLot=&HighLot=&Block=&PropertyCity_input=&PropertyCity=&Building=&Unit=&Split=&LocTownship_input=&LocTownship=&LocSubdivision_input=&LocSubdivision=&ParcelId=&Section_input=&Section=&TownshipRange=&Range=&Quarter_input=&Quarter=&Lot=&SLSection_input=&SLSection=&SLTownship=&TownshipDirection_input=&TownshipDirection=&SLRange=&RangeDirection_input=&RangeDirection=&SLQuarter_input=&SLQuarter=&SLLot=&Partial_input=&Partial=&Half1=&Area=&SLParcelId=&MarriageStartDate=&MarriageEndDate=&OfficiaterName_input=&OfficiaterName="
            print(url)

            driver = self.driver.get(url)
            time.sleep(1)

            # source = self.driver.page_source
            source = json.loads(
                self.driver.find_element(By.TAG_NAME, 'pre').text)
            print(source)  # print source of page

            # Extract 'search' data from the obtained JSON source
            search_data = source.get('search', {})

            # Extract a list of 'Names' from the 'search_data',
            all_output = search_data.get('Names', [])
            # print(len(all_output))

            # Iterate through each result in the list of 'Names' obtained from the 'search_data'
            for result in all_output:
                # Extract the 'InstrumentID' from the current result
                instrument_id = result.get('InstrumentID', '')
                # Append the 'InstrumentID' to the 'process_id' list
                self.process_id.append(instrument_id)
            print(self.process_id)
            print('total_item')
            print(len(self.process_id))

        except Exception as e:
            print(f"Exception occurred in selenium_data: {e}")

    # Extract header details
    def header_detail_page(self, detail_url):
        try:
            driver = self.driver
            # Navigate to the specified detail URL
            self.driver.get(detail_url)

            # Find the 'Act' element on the page
            instrument_no = driver.find_element(By.ID, 'Act')
            # Enable the 'Act' element by removing the 'disabled' attribute using JavaScript
            driver.execute_script(
                "arguments[0].removeAttribute('disabled')", instrument_no)
            time.sleep(1)

            # Fint the page count on the page
            page_count = driver.find_element(By.ID, 'PageCount')
            driver.execute_script(
                "arguments[0].removeAttribute('disabled')", page_count)
            time.sleep(1)

            # Retrieve the value of 'Act' and replace any '-' characters with '0000'
            instrument_no = driver.find_element(By.ID, 'Act')
            document_no = instrument_no.get_attribute(
                "value").replace('-', '0000')

            # Fint the instrument type on the page
            instrument_type = driver.find_element(By.NAME, 'Kind_input')
            driver.execute_script(
                "arguments[0].removeAttribute('disabled')", instrument_type)
            time.sleep(1)

            # Fint the recorded date on the page
            recorded_date = driver.find_element(By.ID, 'InstrumentDate')
            driver.execute_script(
                "arguments[0].removeAttribute('disabled')", recorded_date)
            time.sleep(1)

            # Fint the book on the page
            book = driver.find_element(By.ID, 'Volume')
            driver.execute_script(
                "arguments[0].removeAttribute('disabled')", book)
            time.sleep(1)

            # # Fint the page  on the page
            page = driver.find_element(By.ID, 'Page')
            driver.execute_script(
                "arguments[0].removeAttribute('disabled')", page)
            time.sleep(1)

            # Fint the document date on the page
            document_date = driver.find_element(By.ID, 'ExecutionDate')
            driver.execute_script(
                "arguments[0].removeAttribute('disabled')", document_date)
            time.sleep(1)

            # Fint the number Pages on the page
            numpage = driver.find_element(By.ID, 'PageCount')
            driver.execute_script(
                "arguments[0].removeAttribute('disabled')", numpage)

            # Create a dictionary ('caddo_item') containing details extracted from the page
            caddo_item = {
                "documentType": instrument_type.get_attribute("value"),
                "documentNumber": str(document_no),
                "documentTifName": str(document_no)+".pdf",
                "booksPages": [
                    {"book": book.get_attribute("value"),
                     "page": page.get_attribute("value")}
                ],
                "recordingDate": recorded_date.get_attribute("value"),
                "numberPages": numpage.get_attribute("value"),
                "documentDate": document_date.get_attribute("value"),
                "names": {
                    "grantee":  self.grantee_detail(),
                    "grantor":  self.grantor_detail()
                },
                "legal": self.property_index_detail()
            }
            # print(caddo_item)

        # Return the dictionary
            return caddo_item

        except Exception as e:
            print(f"Exception occurred in header_detail_page: {e}")

# Extract grantor details from the web page
    def grantor_detail(self):

        try:
            driver = self.driver  # local variable
            grantor_list = []  # Initialize an empty list to store grantor details

            table_id = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'VendorsGrid')))
            time.sleep(4)
            # Find the table body within the identified table
            table = table_id.find_element(By.CLASS_NAME, "k-table-tbody")

            # Find all rows within the table body
            rows = table.find_elements(By.TAG_NAME, "tr")
            grantor_list = []

            #  Iterate through each row in the table
            for row in rows:
                # Find all cells (td elements) within the current row
                col = row.find_elements(By.TAG_NAME, "td")
                # print(len(col))

                # Extract the text content of the first cell in the row (column 1)
                col1 = row.find_elements(By.TAG_NAME, "td")[0]
                grantor_list.append(col1.text)

            # Join the list of grantor details into a semicolon-separated string and return
            return ";".join(grantor_list)

        except Exception as e:
            print(f"Exception occurred in grantor_detail: {e}")

    # Extract grantee details from the web page

    def grantee_detail(self):

        try:
            driver = self.driver
            table_id = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'VendeesGrid')))
            time.sleep(4)

            # Find the table body within the identified table
            table = table_id.find_element(By.CLASS_NAME, "k-table-tbody")
            # Find all rows within the table body
            rows = table.find_elements(By.TAG_NAME, "tr")
            # print(len(rows))
            grantee_list = []
            for row in rows:
                # Find all cells (td elements) within the current row
                col = row.find_elements(By.TAG_NAME, "td")
                col1 = row.find_elements(By.TAG_NAME, "td")[0]
                grantee_list.append(col1.text)

            return ";".join(grantee_list)
            # return grantee_list

        except Exception as e:
            print(f"Exception occured in grantee_detail: {e}")

    # Extract property index details from the web page
    def property_index_detail(self):
        driver = self.driver
        result = []
        property_list = []

        try:
            table_id = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'tabstrip-tab-3')))
            time.sleep(4)
            table_id.click()
            table_data = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'tabstrip-3')))
            table = table_data.find_element(By.CLASS_NAME, 'k-table-tbody')
            rows = table.find_elements(By.TAG_NAME, "tr")
            print('property index')

            for row in rows:
                print(row.text)
                property_arr = {}

                # Find all cells (td elements) within the current row
                col = row.find_elements(By.TAG_NAME, "td")
                col1 = row.find_elements(By.TAG_NAME, "td")[0]
                col2 = row.find_elements(By.TAG_NAME, "td")[1]
                col3 = row.find_elements(By.TAG_NAME, "td")[2]
                col4 = row.find_elements(By.TAG_NAME, "td")[3]
                col5 = row.find_elements(By.TAG_NAME, "td")[4]
                col6 = row.find_elements(By.TAG_NAME, "td")[5]
                col7 = row.find_elements(By.TAG_NAME, "td")[6]
                col8 = row.find_elements(By.TAG_NAME, "td")[7]
                print('testing of property index')

                if col1.text != "":
                    property_arr["Section"] = col1.text
                if col2.text != "":
                    property_arr["Township"] = col2.text
                if col3.text != "":
                    property_arr["Township Direction"] = col3.text
                if col4.text != "":
                    property_arr["Range"] = col4.text
                if col5.text != "":
                    property_arr["Range Direction"] = col5.text
                if col6.text != "":
                    property_arr["Quarter"] = col6.text
                if col7.text != "":
                    property_arr["Half"] = col7.text
                if col8.text != "":
                    property_arr["Part"] = col8.text
                property_string = ""
                print('testing complete till if condition')
                # Iterate through the items in property_arr and create a formatted string
                for k, v in property_arr.items():
                    # print(k, v) # keys and value
                    if property_string != "":
                        property_string += " "+str(k) + " "+str(v)
                    else:
                        property_string += str(k) + " "+str(v)
                print(property_string)

                # Append the formatted property string to the property_list
                property_list.append(property_string)

        except:
            # If an exception occurs, set property_list to an empty list
            property_list = []

        # Return the list of property details
        return property_list

    # Click the "View Image" button on the web page

    def click_view_image_button(self, intrument_id):

        try:
            url = "https://caddook.avenuinsights.com/Public/caddook/Home/getFile?InstrumentID=" + \
                str(intrument_id)
            self.driver.get(url)
            driver = self.driver
            driver.implicitly_wait(10)
            time.sleep(10)
            # dv-toolbar-buttons
            # table_id = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'dv-toolbar-button')))
            # table_id.click()

            # Locate and click on the "Print" button using its ID
            table_id = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, 'printButtonDocuVieware1')))
            table_id.click()
            page_range_input = driver.find_element(
                By.XPATH, '//*[@id="inputPrintPageRangeDocuVieware1"]')

            # clear search bar input element
            clear_search_bar_input = driver.find_element(
                By.XPATH, '//*[@id="printPageRangeInputDocuVieware1"]')

            # Click on the page range input
            page_range_input.click()

            clear_search_bar_input.clear()
            # Enter '1' and simulate pressing the ENTER key.
            clear_search_bar_input.send_keys('1', Keys.ENTER)

            # Click on the "Add to Cart" button
            driver.find_element(By.ID, 'addCartButton').click()
            time.sleep(3)

            driver.get(
                "https://caddook.avenuinsights.com/Public/caddook/ShoppingCart")

            time.sleep(2)
            print("Done till the cart button")

        except Exception as e:
            print(f"Exception occured in click_view_image_button: {e} ")

    # Click the "Purchase" button on the web page
    def click_purchase_button(self):

        try:
            shopping_cart_table = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'k-grid-content'))
            )

            print(shopping_cart_table)
            time.sleep(1)

            table = shopping_cart_table.find_element(
                By.CLASS_NAME, "k-table-tbody")
            print(table)

            # Find all rows within the table
            rows = table.find_elements(By.TAG_NAME, "tr")
            # print(len(rows))

            # Initialize a counter variable
            i = 0
            for row in rows:
                # Print the current row
                print(row)
                # Check if it's the first row (index 0)
                if i == 0:
                    # Find the purchase button
                    purchase_button = row.find_elements(By.TAG_NAME, "td")[5]
                    # Click on the "Purchase" button
                    purchase_button.find_element(
                        By.CLASS_NAME, 'k-grid-Print').click()
                    time.sleep(1)

                    # Accept the alert (confirm the purchase) using the web driver
                    self.driver.switch_to.alert.accept()

                else:
                    #  If it's not the first row, continue to the next iteration
                    continue
                i = i+1

        except Exception as e:
            print(f"Exception occured in click_purchase_button: {e}")

    def scrap_data_page(self, instrument_id):
        try:
            print('scrape_id', instrument_id)
            # Call the header_detail_page method to gather information from the details page
            data_item = self.header_detail_page(
                detail_url='https://caddook.avenuinsights.com/Public/caddook/InstrumentGrid/Details?InstrumentID='+str(instrument_id))
            self.json_item.append(data_item)
            self.click_view_image_button(instrument_id)
            self.click_purchase_button()
            self.print_button_after_purchase()
            time.sleep(4)
            img_status = self.rename_downloaded_file(
                data_item['documentNumber'], instrument_id)

            # # Append the gathered data to the json_item list
            # if img_status == 1:
            #     self.json_item.append(data_item)
        except Exception as e:
            print(f"Exception occurred in scrape_data_page: {e}")
            self.missing_id.append(instrument_id)

    def scrap_data(self):

        try:
            # Check if there are instrument IDs to process
            print("total items")
            print(len(self.process_id))
            if len(self.process_id) > 0:
                icnt = 0

                for intrument_id in self.process_id:
                    self.scrap_data_page(intrument_id)
                    time.sleep(1)

                    # if icnt < 1:
                    #     self.scrap_data_page(intrument_id)
                    #     time.sleep(2)

                    # else:
                    #     continue
                    # icnt = icnt + 1

                # Check if any data has been gathered
                if len(self.json_item) > 0:
                    print(self.json_item)

                    # Create a file path based on the current date for the JSON file
                    current_date = datetime.now().strftime("%Y%m%d")
                    file_path = str(current_date)+'_caddo_county_land.json'
                    self.to_json(file_path)
                    print(" Scraping process is complete , All done ")
                    print("missing id")
                    print(len(self.missing_id))

                    print(self.missing_id)
                elif len(self.missing_id) > 0:
                    self.process_id = self.missing_id
                    self.missing_id = []
                    self.scrap_data()
                    # for instrument_id in self.missing_id:
                    #     self.scrap_data_page(intrument_id)
                    #     time.sleep(1)

                # self.driver.quit()
        except Exception as e:
            print(f"Exception occured in scrap_data: {e}")

# Renames the downloaded file
    def rename_downloaded_file(self, documentNumber, instrument_id):

        try:
            # Get the download directory and list all files in it
            download_directory = self.file_dir
            files = os.listdir(download_directory)
            print(files)

            # Define the existing and new file names
            exist_file = "print.pdf"
            new_file_name = str(documentNumber).replace('-', '0000')+'.pdf'

            # Create the source and destination file paths
            src_file = os.path.join(download_directory, exist_file)
            dst_file = os.path.join(download_directory, new_file_name)
            # Rename the file
            os.rename(os.path.join(download_directory, src_file),
                      os.path.join(download_directory, dst_file))

            time.sleep(5)
            print("Renaming process is complete")
            return 1

        except Exception as e:
            print(f"Exception occured in rename_downloaded_file: {e}")
            self.missing_id.append(instrument_id)
            return 0

# Clicks the print button after making a purchase
    def print_button_after_purchase(self):

        try:
            print(self.driver.current_url)
            time.sleep(2)

            # Switch to the second window handle
            self.driver.switch_to.window(self.driver.window_handles[1])
            print(self.driver.current_url)

            time.sleep(2)
            driver = self.driver
            driver.implicitly_wait(15)
            driver.current_url
            print(driver.current_url)
            print(self.driver.current_url)

        # Find and click on the print button i
            print_id = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'printButtonDocuVieware1')))
            print_id.click()
            select_pdf = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="print_destination_selectDocuVieware1-button"]/span[2]')))
            select_pdf.click()
            time.sleep(3)

            # Select the PDF option from the dropdown
            driver.find_element(By.ID, 'dvUi-id-3').click()

            page_range = driver.find_element(
                By.XPATH, '//*[@id="inputPrintPageRangeDocuVieware1"]')
            # page_range = driver.find_element(
            #     By.XPATH, '//*[@id="inputPrintPagesSelectedDocuVieware1"]')
            # inputPrintPagesSelectedDocuVieware1
            clear_search_bar = driver.find_element(
                By.XPATH, '//*[@id="printPageRangeInputDocuVieware1"]')
            page_range.click()
            # clear_search_bar.clear()

            clear_search_bar.send_keys('1', Keys.ENTER)
            # Click on the print button
            driver.find_element(By.ID, 'printButton').click()
            driver.find_element(By.ID, 'addCartButton').click()

            # addCartButton
            time.sleep(2)

            print("purchase is complete")

        except Exception as e:
            print(f"Exception occured in print_button_after_purchase {e}")

    def to_json(self, json_filename='output.json'):

        try:
            json_filename = self.file_dir+"/"+json_filename
            fp = open(json_filename, "w")

            # Iterate through each dictionary in self.json_item
            inc = 0
            for dict in self.json_item:
                # Convert the dictionary to a JSON string
                json_data = json.dumps(dict)
                print(json_data)

                # Write the JSON data to the file with a newline
                if inc == 0:
                    fp.write(str(json_data))
                else:
                    fp.write("\n"+str(json_data))
                inc = inc + 1
            print(f'Data written to {json_filename}')

        except Exception as e:
            print(f"Exception occured in to_json: {e}")

    def main(self):
        try:
            # base_folder = "/var/www/html/py/ob_occ/output/caddocounty/land/"
            # capture.create_folder_with_current_date(base_folder)

            capture.login('', '')

            capture.selenium_data()  # comment this for process id
            time.sleep(1)
            capture.scrap_data()

        except Exception as e:
            print(f"Exception occured in main: {e}")

        finally:
            self.driver.quit()


if __name__ == "__main__":
    capture = Capture()
    capture.main()

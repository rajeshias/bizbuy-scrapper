import csv
import json
import time
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains

'''input data'''
chrome_driver_location = '../chromedriver.exe'  # download url: https://chromedriver.chromium.org/downloads
output_path = ''                                # leave blank for using the same path as the script

options = webdriver.ChromeOptions()
# options.add_argument('--headless')
# options.add_argument("--start-maximized")
driver = webdriver.Chrome(chrome_driver_location, options=options)

action = ActionChains(driver)
wait = WebDriverWait(driver, 200)


def scrap(data):
    """
    where the data extraction happens for each businesses
    """
    headers = ['Business Name', 'Location', 'County', 'Asking Price', 'Cash Flow', 'Price per sqft', 'NOI',
               'Year Built', 'Gross Revenue', 'EBITDA', 'Furniture, Fixtures, & Equipment (FF&E)',
               'Inventory', 'Rent', 'Established', 'Inital Fee', 'Capital Required', 'Short Description',
               'Long Description', 'Real Estate',
               'Building SF', 'Lease Expiration', 'Employees', 'Facilities', 'Competition', 'Growth & Expansion',
               'Financing', 'Support & Training', 'Reason for Selling', 'Franchise', 'Ad#', 'Listed By', 'Phone No']
    rows = [headers]
    for adno, details in data.items():
        driver.get(details['url'])
        scrap_title = details['name']
        location = driver.find_element_by_xpath('//h2[@class="gray"]').text
        if '(' in location:
            scrap_location = location.split('(')[0]
            scrap_county = location.split('(')[1][:-1]
        else:
            scrap_location = location
            scrap_county = ''
        details = driver.find_element_by_xpath('//div[@class="row-fluid lgFinancials"]')
        detailsHeaders = details.find_elements_by_xpath('.//span[@class="title"]')
        detailsValues = details.find_elements_by_xpath('.//b')
        details_dict = {}
        for i, j in zip(detailsHeaders, detailsValues):
            details_dict[i.text] = j
        scrap_askingPrice = details_dict['Asking Price:'].text if 'Asking Price:' in details_dict.keys() else ''
        scrap_cashFlow = details_dict['Cash Flow:'].text if 'Cash Flow:' in details_dict.keys() else ''
        scrap_grossRevenue = details_dict['Gross Revenue:'].text if 'Gross Revenue:' in details_dict.keys() else ''
        scrap_intitalFee = details_dict['Initial Fee:'].text if 'Initial Fee:' in details_dict.keys() else ''
        scrap_capitalReqd = details_dict["Capital Req'd:"].text if "Capital Req'd:" in details_dict.keys() else ''

        more_details = driver.find_element_by_xpath('//div[@class="row-fluid"]')
        more_detailsHeaders = more_details.find_elements_by_xpath('.//span[@class="title"]')
        more_detailsValues = more_details.find_elements_by_xpath('.//b')
        more_details_dict = {}
        for i, j in zip(more_detailsHeaders, more_detailsValues):
            more_details_dict[i.text] = j
        scrap_pricepersqft = more_details_dict[
            "Price/Sq. Ft.:"].text if "Price/Sq. Ft.:" in more_details_dict.keys() else ''
        scrap_NOI = more_details_dict["NOI:"].text if "NOI:" in more_details_dict.keys() else ''
        scrap_yearBuilt = more_details_dict["Year Built:"].text if "Year Built:" in more_details_dict.keys() else ''
        scrap_grossRevenue = more_details_dict[
            "Gross Revenue:"].text if "Gross Revenue:" in more_details_dict.keys() else scrap_grossRevenue
        scrap_EBITDA = more_details_dict["EBITDA:"].text if "EBITDA:" in more_details_dict.keys() else ''
        scrap_FFandE = more_details_dict["FF&E:"].text if "FF&E:" in more_details_dict.keys() else ''
        scrap_inventory = more_details_dict["Inventory:"].text if "Inventory:" in more_details_dict.keys() else ''
        scrap_rent = more_details_dict["Rent:"].text if "Rent:" in more_details_dict.keys() else ''
        scrap_established = more_details_dict["Established:"].text if "Established:" in more_details_dict.keys() else ''
        scrap_realEstate = more_details_dict["Real Estate:"].text if "Real Estate:" in more_details_dict.keys() else ''

        scrap_shortDescription = driver.find_element_by_xpath('//b[@class="profileAdLine"]').text
        scrap_longDiscription = driver.find_element_by_xpath('//div[@class="businessDescription"]').text

        try:
            detail_information = driver.find_element_by_xpath('//dl[@class="listingProfile_details"]')
            detailHeaders = detail_information.find_elements_by_xpath('.//strong')
            detailValues = detail_information.find_elements_by_xpath('.//dd')
            detail_dict = {}
            for i, j in zip(detailHeaders, detailValues):
                detail_dict[i.text[:-1]] = j
        except selenium.common.exceptions.NoSuchElementException:
            detail_dict = {}

        scrap_realEstate = detail_dict['Real Estate'].text if 'Real Estate' in detail_dict.keys() else scrap_realEstate
        scrap_buildigSF = detail_dict['Building SF'].text if 'Building SF' in detail_dict.keys() else ''
        scrap_leaseExpiration = detail_dict['Lease Expiration'].text if 'Lease Expiration' in detail_dict.keys() else ''
        scrap_employees = detail_dict['Employees'].text if 'Employees' in detail_dict.keys() else ''
        scrap_facilities = detail_dict['Facilities'].text if 'Facilities' in detail_dict.keys() else ''
        scrap_competition = detail_dict['Competition'].text if 'Competition' in detail_dict.keys() else ''
        scrap_growth = detail_dict['Growth & Expansion'].text if 'Growth & Expansion' in detail_dict.keys() else ''
        scrap_financing = detail_dict['Financing'].text if 'Financing' in detail_dict.keys() else ''
        scrap_training = detail_dict['Support & Training'].text if 'Support & Training' in detail_dict.keys() else ''
        scrap_reason = detail_dict['Reason for Selling'].text if 'Reason for Selling' in detail_dict.keys() else ''
        scrap_franchise = detail_dict['Franchise'].text if 'Franchise' in detail_dict.keys() else ''

        scrap_listedBy = driver.find_element_by_xpath('//div[@class="broker"]').text.replace('Phone Number',
                                                                                             '').replace(
            'Business Listed By:', '').replace('View My Listings', '').replace('Startup Listed By:', '').replace(
            'Property Listed By:', '').strip()
        try:
            scrap_phoneNo = \
                driver.find_element_by_xpath('//label[@class="ctc_phone"]').find_element_by_xpath('.//a').get_attribute(
                    'href').split(':')[-1].strip()
        except selenium.common.exceptions.NoSuchElementException:
            scrap_phoneNo = ''

        rows.append([scrap_title, scrap_location, scrap_county, scrap_askingPrice, scrap_cashFlow, scrap_pricepersqft,
                     scrap_NOI, scrap_yearBuilt, scrap_grossRevenue, scrap_EBITDA, scrap_FFandE,
                     scrap_inventory, scrap_rent, scrap_established, scrap_intitalFee, scrap_capitalReqd,
                     scrap_shortDescription, scrap_longDiscription, scrap_realEstate,
                     scrap_buildigSF, scrap_leaseExpiration, scrap_employees, scrap_facilities, scrap_competition,
                     scrap_growth,
                     scrap_financing, scrap_training, scrap_reason, scrap_franchise, adno, scrap_listedBy,
                     scrap_phoneNo])
    return rows


def checkallpages(city):
    data = {}
    print(f'Checking for new businesses for sale in {city}...')
    page = 1
    while page != 0:
        driver.get(
            f"https://www.bizbuysell.com/{city.lower().replace(' ', '-')}-businesses-for-sale/{page}")
        time.sleep(1)
        try:
            cards = driver.find_elements_by_xpath('//a[@class="diamond"]')
        except:
            cards = driver.find_elements_by_xpath('//a[@class="showcase"]')
        for card in cards:
            if card.get_attribute('id') in data.keys():
                page = -1
            if len(str(card.get_attribute('id'))) > 4:
                data[card.get_attribute('id')] = {
                    'url': card.get_attribute('href'),
                    'name': card.get_attribute('title')
                }
        page += 1
    return data


if __name__ == "__main__":
    cities = []
    with open("citylist.csv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for line in reader:
            cities.append(line[0])

    allRows = []
    for city in cities:
        try:
            with open(output_path + f"{city.replace(' ', '-')}.json", "r") as f:
                prevData = json.load(f)
            data = checkallpages(city)
            newBusiness = 0
            newData = {}
            for adno in data.keys():
                if adno in prevData.keys():
                    pass
                else:
                    newBusiness += 1
                    newData[adno] = data[adno]

            if newBusiness:
                print(f'Found {newBusiness} new businesses in {city}. Updating spread sheet!')
                # updating spreadsheet
                with open(output_path + f"{city.replace(' ', '-')}.csv", "a") as fp:
                    wr = csv.writer(fp, lineterminator='\n')
                    wr.writerows(scrap(newData))
                # updating meta data in json
                with open(output_path + f"{city.replace(' ', '-')}.json", "w") as f:
                    json.dump(data, f)

            else:
                print(f'No new business pages found in {city}, all businesses in the spreadsheet are up to date!')
                quit()
        except FileNotFoundError:
            print("Scrapping...")
            data = checkallpages(city)
            finalData = scrap(data)

            # create a json meta data file
            with open(output_path + f"{city.replace(' ', '-')}.json", "w") as f:
                json.dump(data, f)
            # export scrapped data
            with open(output_path + f"{city.replace(' ', '-')}.csv", "w") as fp:
                wr = csv.writer(fp, lineterminator='\n')
                wr.writerows(finalData)

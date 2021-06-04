import csv
import time
import random
from collections import defaultdict
import pandas as pd
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

def randomsleep():
    time.sleep(random.randint(1, 6))
    
    
def checkprogress(city, data):
    try:
        df = pd.read_excel(output_path + f"{city.replace(' ', '-')}.xlsx")
        for i in df['Ad#']:
            # try:
            del data[str(int(i))]
            # except KeyError:
            #     pass
        if not len(data.keys()):
            print(f'{city} Up-to-date\n')
            choice0 = input('Would you like to check for new listings again?(y/n)')
            if choice0.lower() == 'y':
                return defaultdict(list), 0
            else:
                quit()
        else:
            print("resuming right where you left!")
            print(len(data.keys()), ' more to go...')
        return df.to_dict(orient='list'), len(df.index)
    except FileNotFoundError or KeyError:
        return defaultdict(list), 0

def scrap(data, city):
    """
    where the data extraction happens for each business
    """
    pd.set_option('display.max_columns', None)
    scrap, count = checkprogress(city, data)
    for adno, details in data.items():
        randomsleep()
        driver.get(details['url'])
        span8Element = driver.find_element_by_xpath('//div[@class="span8"]').text
        if 'This listing is no longer available.' in span8Element:
            continue
        scrap['URL'].append(details['url'])
        scrap['Name'].append(details['name'])
        scrap['Ad#'].append(adno)
        scrap['Location'].append(span8Element)
        section1 = driver.find_element_by_xpath('//div[@class="row-fluid b-margin financials clearfix"]')
        section1Headers = section1.find_elements_by_xpath('.//span[@class="title"]')
        section1Values = section1.find_elements_by_xpath('.//b')

        try:
            details = driver.find_element_by_xpath('//dl[@class="listingProfile_details"]')
            detailsHeaders = details.find_elements_by_xpath('.//dt')
            detailsValues = details.find_elements_by_xpath('.//dd')
        except:
            detailsHeaders = []
            detailsValues = []

        if len(detailsValues) > len(detailsHeaders):
            del detailsValues[2]

        for i, j in zip(section1Headers, section1Values):
            if i.text[:-1] not in scrap.keys():
                scrap[i.text[:-1]] = []

        for i, j in zip(detailsHeaders, detailsValues):
            if 'details_' + i.text[:-1] not in scrap.keys():
                scrap['details_' + i.text[:-1]] = []

        for i, j in scrap.items():
            while len(j) < count:
                scrap[i].append('')

        for i, j in zip(section1Headers, section1Values):
            scrap[i.text[:-1]].append(j.text)
        for i, j in zip(detailsHeaders, detailsValues):
            scrap['details_' + i.text[:-1]].append(j.text)

        try:
            scrap['Short Description'].append(driver.find_element_by_xpath('//b[@class="profileAdLine"]').text)
        except:
            scrap['Short Description'].append('')
        try:
            scrap['Long Description'].append(driver.find_element_by_xpath('//div[@class="businessDescription"]').text)
        except:
            scrap['Long Description'].append('')
        try:
            scrap['listedBy'].append(driver.find_element_by_xpath('//div[@class="broker"]').text.replace('Phone Number',
                                                                                                 '').replace(
                'Business Listed By:', '').replace('View My Listings', '').replace('Startup Listed By:', '').replace(
                'Property Listed By:', '').strip())
        except:
            scrap['listedBy'].append('')
        try:
            scrap['phoneNo'].append(driver.find_element_by_xpath('//label[@class="ctc_phone"]').find_element_by_xpath('.//a').get_attribute(
                    'href').split(':')[-1].strip())
        except selenium.common.exceptions.NoSuchElementException:
            scrap['phoneNo'].append('')


        dataFrame = pd.DataFrame.from_dict(scrap, orient='index')
        dataFrame = dataFrame.transpose()
        # dataFrame = dataFrame.reindex(sorted(dataFrame.columns), axis=1)
        # escape illegal characters
        dataFrame = dataFrame.applymap(lambda x: x.encode('unicode_escape').
                                       decode('utf-8') if isinstance(x, str) else x)
        # print(dataFrame)
        dataFrame.to_excel(output_path + f"{city.replace(' ', '-')}.xlsx")
        count += 1

def checkallpages(city):
    page = 1
    data = {}
    try:
        resume = pd.read_excel(output_path + f"{city.replace(' ', '-')}_progress.xlsx").to_dict()
        choice0 = input(f'Would you like to resume where you left?(y/n):')
        if choice0.lower() == 'y':

            # retrieve previous pagination data
            for index, adno in enumerate(list(resume['Unnamed: 0'].values())):
                data[str(adno)] = {
                    'url': list(resume['url'].values())[index],
                    'name': list(resume['name'].values())[index],
                    'pageno': list(resume['pageno'].values())[index]
                }
            if list(resume['pageno'].values())[-1] == 'complete':
                return data
            page = int(list(resume['pageno'].values())[-1])
            print(f'Resuming from page {page}')
        else:
            quit()

    except FileNotFoundError:
        pass

    print(f'Checking for new businesses for sale in {city}...')

    while page != 0:
        randomsleep()
        driver.get(
            f"https://www.bizbuysell.com/{city.lower().replace(' ', '-')}-businesses-for-sale/{page}?q=bHQ9MzAsNDAsODA%3D")
        time.sleep(1)
        cards = []
        try:
            cards += (driver.find_elements_by_xpath('//a[@class="diamond"]'))
        except:
            pass
        try:
            cards += (driver.find_elements_by_xpath('//a[@class="showcase"]'))
        except:
            pass
        try:
            cards += (driver.find_elements_by_xpath('//a[@class="basic"]'))
        except:
            pass
        pageno = page
        for card in cards:
            if card.get_attribute('id') in data.keys():
                page = -1
                pageno = 'complete'
            if 4 < len(str(card.get_attribute('id'))) < 12:  # to get rid of auctions and franchise!
                data[card.get_attribute('id')] = {
                    'url': card.get_attribute('href'),
                    'name': card.get_attribute('title'),
                    'pageno': pageno
                }
        paginationDF = pd.DataFrame.from_dict(data)
        paginationDF = paginationDF.transpose()
        # print(paginationDF)
        paginationDF.to_excel(output_path + f"{city.replace(' ', '-')}_progress.xlsx")
        page += 1
    return data


if __name__ == "__main__":

    # get all state names from csv
    cities = []
    with open("citylist.csv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for line in reader:
            cities.append(line[0])
    if not cities:
        print("Error: No states listed!")
        quit()

    allRows = []
    for city in cities:
        print("Scrapping...")
        data = checkallpages(city)
        scrap(data, city)

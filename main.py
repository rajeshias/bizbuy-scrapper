import csv
import json
import time
import datetime
from collections import defaultdict
from pprint import pprint

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

def checkprogress(city, data):
    try:
        df = pd.read_excel(output_path + f"{city.replace(' ', '-')}.xlsx")
        for i in df['Ad#']:
            del data[str(int(i))]
        print(len(data.keys()), ' more to go...')
        if not len(data.keys()):
            print(f'{city} Up-to-date')
        return df.to_dict(orient='list'), len(df.index)
    except FileNotFoundError:
        return defaultdict(list), 0

def scrap(data, city):
    """
    where the data extraction happens for each businesses
    """
    pd.set_option('display.max_columns', None)
    scrap, count = checkprogress(city, data)
    for adno, details in data.items():
        driver.get(details['url'])
        scrap['URL'].append(details['url'])
        scrap['Name'].append(details['name'])
        scrap['Ad#'].append(adno)
        scrap['Location'].append(driver.find_element_by_xpath('//div[@class="span8"]').text)
        section1 = driver.find_element_by_xpath('//div[@class="row-fluid b-margin financials clearfix"]')
        section1Headers = section1.find_elements_by_xpath('.//span[@class="title"]')
        section1Values = section1.find_elements_by_xpath('.//b')
        for i, j in zip(section1Headers, section1Values):
            scrap[i.text[:-1]].append(j.text)

        details = driver.find_element_by_xpath('//dl[@class="listingProfile_details"]')
        detailsHeaders = details.find_elements_by_xpath('.//dt')
        detailsValues = details.find_elements_by_xpath('.//dd')
        if len(detailsValues) > len(detailsHeaders):
            del detailsValues[2]
        for i, j in zip(detailsHeaders, detailsValues):
            scrap['details_' + i.text[:-1]].append(j.text)

        scrap['Short Description'].append(driver.find_element_by_xpath('//b[@class="profileAdLine"]').text)
        scrap['Long Description'].append(driver.find_element_by_xpath('//div[@class="businessDescription"]').text)



        scrap['listedBy'].append(driver.find_element_by_xpath('//div[@class="broker"]').text.replace('Phone Number',
                                                                                             '').replace(
            'Business Listed By:', '').replace('View My Listings', '').replace('Startup Listed By:', '').replace(
            'Property Listed By:', '').strip())
        try:
            scrap['phoneNo'].append(driver.find_element_by_xpath('//label[@class="ctc_phone"]').find_element_by_xpath('.//a').get_attribute(
                    'href').split(':')[-1].strip())
        except selenium.common.exceptions.NoSuchElementException:
            scrap['phoneNo'].append('')

        for i, j in scrap.items():
            while len(j) < count+1:
                scrap[i].append('')

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
    data = {}
    print(f'Checking for new businesses for sale in {city}...')
    page = 1
    while page != 0:
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
        for card in cards:
            if card.get_attribute('id') in data.keys():
                page = -1
            if len(str(card.get_attribute('id'))) > 4:
                data[card.get_attribute('id')] = {
                    'url': card.get_attribute('href'),
                    'name': card.get_attribute('title')
                }
        page += 1
        # break #get rid
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

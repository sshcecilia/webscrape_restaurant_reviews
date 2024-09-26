from webscraping import webscrape_restaurants
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

def access_webpage(url):
    """
    Open and return the driver to the url provided

    :param url (str): url of a website 
    """
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(300)
    driver.get(url)
    time.sleep(3)
    try:
        driver.maximize_window()
    except (TimeoutException, NoSuchElementException):
        pass
    return driver

def get_streetname(driver):
    """
    Extract the list of streetname from the website

    :param driver: driver object of the website
    """
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'li')))   
    raw = driver.find_elements(By.CSS_SELECTOR, "li")
    street = map(lambda x: x.text, raw)
    return street

def initial_setup(restaurant_dir, review_dir, streetname_dir, initial):
    """
    Set up the necessary files to store the extracted information and the files are returned as Pandas DataFrame

    :param restaurant_dir (str): directory to get or store the restaurants data
    :param review_dir (str): directory to get or store the reviews data
    :param streetname_dir (str): directory to get or store the streetname data
    :param initial (boolean):   whether it is the first file setup
                                if yes, create the file, else access the files
    """
    if initial == False:
        restaurants = pd.read_csv(restaurant_dir, keep_default_na=False)
        reviews = pd.read_csv(review_dir)
        streetname = pd.read_csv(streetname_dir, keep_default_na=False)

    else:
        ## Creation of DataFrame to Store Restaurant Information
        restaurants = pd.DataFrame({'restaurant_name': pd.Series(dtype='str'),
                                    'href': pd.Series(dtype='str'),
                                    'status': pd.Series(dtype='str'),
                                    'info': pd.Series(dtype='str'),
                                    'type': pd.Series(dtype='str'),
                                    'price_label': pd.Series(dtype='str'),
                                    'price_level': pd.Series(dtype='str'),
                                    'address': pd.Series(dtype='str'),
                                    'website': pd.Series(dtype='str'),
                                    'lat_long': pd.Series(dtype='str'),
                                    'op_hours': pd.Series(dtype='str'),
                                    'poptime': pd.Series(dtype='str'),
                                    'services': pd.Series(dtype='str'),
                                    'details_last_updated': pd.Series(dtype='str'),
                                    'reviews_last_updated': pd.Series(dtype='str')})
        
        reviews = pd.DataFrame({'restaurant_name': pd.Series(dtype='str'),
                                'review_id': pd.Series(dtype='str'),
                                'user_info': pd.Series(dtype='str'),
                                'user_href': pd.Series(dtype='str'),
                                'rating': pd.Series(dtype='str'),
                                'review': pd.Series(dtype='str')})

        ## Extraction of List of Streetname in Singapore
        driver = access_webpage(url = "https://geographic.org/streetview/singapore/index.html")
        streetname = pd.DataFrame(['Singapore'], columns = ['street'])
        streetname = pd.concat([streetname, pd.DataFrame(get_streetname(driver), columns = ['street'])], sort = False, ignore_index = True)
        streetname.drop_duplicates(inplace = True)
        streetname[['last_updated']] = date(1900,1,1)
        driver.close()

        restaurants.to_csv(restaurant_dir, index = False)
        reviews.to_csv(review_dir, index = False)
        streetname.to_csv(streetname_dir, index = False)

    return restaurants, reviews, streetname
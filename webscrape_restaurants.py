from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd


def access_webpage(url):
    """
    Open and return the driver to the url provided

    :param url: string object containing url of a website 
    """

    driver = webdriver.Chrome()
    driver.set_page_load_timeout(300)
    driver.get(url)

    return driver
       

def search_scroll(driver, query, num_scroll = -1):
    """
    Search based on the query provided and scroll down the website to get the full list of restaurants

    :param driver: webdriver object
    :param query: keyword to enter into the searchbox
    :param num_scroll: int containing the number of times to scroll. default is -1 to scroll until the end of the page.
    """
    wait = WebDriverWait(driver, 10)
    searchbox = wait.until(EC.visibility_of_element_located((By.ID, 'searchboxinput')))

    searchbox.clear()
    searchbox.send_keys(query)
    searchbox.send_keys(Keys.RETURN)

    divSideBar = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,f"div[aria-label='Results for " + query + "']")))

    keepScrolling = True
    while(keepScrolling):
        driver.execute_script('arguments[0].scrollTo(0, arguments[0].scrollHeight)', divSideBar)
        time.sleep(1.2)
        html = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "html"))).get_attribute('outerHTML')
        if ((html.find("You've reached the end of the list.") != -1) | i == 0):
            keepScrolling = False
        num_scroll -= 1

def extract_restaurants(driver):
    """
    Extract the following into a Pandas Dataframe
    - Name of the restaurants
    - Google maps link of the restaurant
    - Status of the restaurant (whether the store is operating)
    - Ratings and Number of reviews

    :param driver: webdriver object
    """
    data = pd.DataFrame(columns = ['id', 'name', 'href', 'status', 'info'])
    raw = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")

    for i in range(len(raw)):

        # Skip extracting restaurant if link has been scraped. Avoid duplicate copies of the same restaurant.
        if sum(data['href'].isin([raw[i].find_elements(By.CSS_SELECTOR, "a.hfpxzc")[0].get_attribute('href')])) >= 1: 
            continue

        # If Status is not available, set it to 'Open'. If number of reviews are not available
        elif (len(raw[i].find_elements(By.CSS_SELECTOR, "span.eXlrNe")) == 0):
            data = pd.concat([data, pd.DataFrame({'id': i, 'name': raw[i].find_elements(By.CSS_SELECTOR, "a.hfpxzc")[0].get_attribute('aria-label'), 'href': [raw[i].find_elements(By.CSS_SELECTOR, "a.hfpxzc")[0].get_attribute('href')], 'status': ['Open'], 'info': [raw[i].find_elements(By.CSS_SELECTOR, "span.ZkP5Je")[0].get_attribute('aria-label')]})], ignore_index = True)

        else:
            data = pd.concat([data, pd.DataFrame({'id': i, 'name': raw[i].find_elements(By.CSS_SELECTOR, "a.hfpxzc")[0].get_attribute('aria-label'), 'href': [raw[i].find_elements(By.CSS_SELECTOR, "a.hfpxzc")[0].get_attribute('href')], 'status': [raw[i].find_elements(By.CSS_SELECTOR, "span.eXlrNe")[0].text], 'info': [raw[i].find_elements(By.CSS_SELECTOR, "span.ZkP5Je")[0].get_attribute('aria-label')]})], ignore_index = True) 

    return data

driver = access_webpage(url = "https://www.google.com/maps")
search_scroll(driver, query = "Food in Singapore")
data = extract_restaurants(driver)
driver.close()
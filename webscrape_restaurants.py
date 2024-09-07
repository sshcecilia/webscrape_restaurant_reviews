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
        if ((html.find("You've reached the end of the list.") != -1) | num_scroll == 0):
            keepScrolling = False
        num_scroll -= 1

def extract_basic(element):
    """
    Extract the following information of a restaurant
    - Name of the restaurants
    - Google maps link of the restaurant
    - Status of the restaurant (whether the store is operating)
    - Ratings and Number of reviews

    :param driver: An element of a webpage
    """
    name = element.find_elements(By.CSS_SELECTOR, "a.hfpxzc")[0].get_attribute('aria-label')
    href = element.find_elements(By.CSS_SELECTOR, "a.hfpxzc")[0].get_attribute('href')
    info = element.find_elements(By.CSS_SELECTOR, "span.ZkP5Je")[0].get_attribute('aria-label')
    
    # If Status is not available, set it to 'Open'. If number of reviews are not available
    if (len(element.find_elements(By.CSS_SELECTOR, "span.eXlrNe")) == 0):
        status = 'Open'
    else:
        status = element.find_elements(By.CSS_SELECTOR, "span.eXlrNe")[0].text
    return name, href, status, info

def restaurant_list(driver):
    """
    Obtain a list of elements for the restaurants extracted from the webpage
    
    :param driver: webdriver object
    """
    raw = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
    return raw
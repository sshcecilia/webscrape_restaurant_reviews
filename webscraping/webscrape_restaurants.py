import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from datetime import date
import pandas as pd
from webscraping import file_setup

class restaurants():
    """
    Obtain a list of restaurants near specific region from Google Maps
        
    :param region (str): region in which the nearby restaurants will be extracted
    :param max_scroll (int): the number of times to scroll
                             default value is -1 which will scroll till the end of the page
    :param max_tries (int): the number of times to retry scrolling the webpage should the webpage takes too long to load
                            default value is 5
    """
    def __init__(self, region, max_scroll = -1, max_tries = 5):
        self.driver = file_setup.access_webpage(url = "https://www.google.com/maps")
        self.region = region
        self.max_scroll = max_scroll
        self.max_tries = max_tries

    def restaurant_list(self):
        """
        Obtain a list of elements for the restaurants extracted from the webpage
        """
        raw = self.driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
        return raw

    def search_scroll(self, query):
        """
        Search based on the query provided and
            scroll down the website to get the full list of restaurants

        :param query (str): keyword to enter into the searchbox
        """
        wait = WebDriverWait(self.driver, 30)
        searchbox = wait.until(
                        EC.visibility_of_element_located(
                            (By.ID, 'searchboxinput')))

        searchbox.clear()
        searchbox.send_keys(query)
        searchbox.send_keys(Keys.RETURN)

        sidebar = wait.until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "div[aria-label='Results for " + query + "']")))

        keepscrolling = True
        num_restaurants = 0
        prev_num_restaurants = 0
        counter = 0
        while keepscrolling:
            self.driver.execute_script('arguments[0].scrollTo(0, arguments[0].scrollHeight)',
                                sidebar)
            time.sleep(1.2)
            html = wait.until(
                    EC.visibility_of_element_located(
                        (By.TAG_NAME, "html"))).get_attribute('outerHTML')
            prev_num_restaurants = num_restaurants
            num_restaurants = len(self.restaurant_list())  
            if (html.find("You've reached the end of the list.") != -1) | self.max_scroll == 0:
                keepscrolling = False
            elif counter >= self.max_tries:
                keepscrolling = False
            elif num_restaurants == prev_num_restaurants:
                counter += 1
            self.max_scroll -= 1

    def get_basic(self, element):
        """
        Extract the following information of a restaurant
        - Name of the restaurants
        - Google maps link of the restaurant
        - Status of the restaurant (whether the store is operating)
        - Ratings and Number of reviews

        :param element: An element of a webpage
        """
        try:
            name = element.find_elements(By.CSS_SELECTOR,"a.hfpxzc")[0].get_attribute('aria-label')
            href = element.find_elements(By.CSS_SELECTOR, "a.hfpxzc")[0].get_attribute('href')
            info = element.find_elements(By.CSS_SELECTOR, "span.ZkP5Je")[0].get_attribute('aria-label')

            # If Status is not available, set it to 'Open'. If number of reviews are not available
            if len(element.find_elements(By.CSS_SELECTOR, "span.eXlrNe")) == 0:
                status = 'Open'
            else:
                status = element.find_elements(By.CSS_SELECTOR, "span.eXlrNe")[0].text
        except:
            name = ''
            href = ''
            status = ''
            info = ''
    
        return name, href, status, info

    ## Extraction of List of Restaurants

    def get_restaurant(self):
        """
        Compile the extracted information into a Pandas DataFrame and update when the information was last updated
        Close the driver once the task is completed
        """
        try:
            self.search_scroll(f"Food in {self.region}")
            restaurants_element = self.restaurant_list()
            restaurants_subset = pd.DataFrame(map(self.get_basic, restaurants_element), columns = ['restaurant_name', 'href', 'status', 'info'])
            restaurants_subset.drop(restaurants_subset[restaurants_subset['href'] == ''].index, inplace=True)
            restaurants_subset[['details_last_updated']] = date(1900,1,1)
            restaurants_subset[['reviews_last_updated']] = date(1900,1,1)
        except TimeoutException:
            restaurants_subset = None

        self.driver.close()
        return restaurants_subset
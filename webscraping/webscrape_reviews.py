from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import file_setup
import pandas as pd

class reviews():
    """
    Extract customers' reviews of a restaurant from Google Maps

    :param href (str): web link to the restaurant's Google Map page
    :param restaurant_name (str): name of the restaurant from the restaurant database
    :param max_scroll (int): the number of times to scroll
                             default value is -1 which will scroll till the end of the page
    :param max_tries (int): the number of times to retry scrolling the webpage should the webpage takes too long to load
                            default value is 5
    :param min_length (int): Ooly extract customer's reviews within a year or at least min_length number of reviews whichever larger
                             default value is 300
    """
    def __init__(self, href, restaurant_name, max_scroll = -1, max_tries = 5, min_length = 300):
        self.driver = file_setup.access_webpage(href)
        self.max_scroll = max_scroll
        self.wait = WebDriverWait(self.driver, 30)
        self.max_tries = max_tries
        self.min_length = min_length
        self.restaurant_name = restaurant_name

    def expand_reviews(self):
        """
        To scroll down to obtain all the reviews and expand them out to ensure all information are captured
        """
        element = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(), 'Reviews')]")))
        element.click()
        time.sleep(3)

        element = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Sort')]")))
        element.click()

        element = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@data-index = '1']")))
        element.click()

        ## Scroll down 
        divSideBar = self.driver.find_element(By.XPATH, "//div[(contains(@class, 'm6QErb')) and (@tabindex = '-1')]")
        keepScrolling = True
        current_length = 0
        prev_length = 0
        counter = 0

        while(keepScrolling):
            self.driver.execute_script('arguments[0].scrollTo(0, arguments[0].scrollHeight)', divSideBar)
            time.sleep(0.8)
            prev_length = current_length
            current_length = len(self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'rsqaWe']"))))
            if self.max_scroll == 0:
                keepScrolling = False
            elif counter >= self.max_tries:
                keepScrolling = False
            elif current_length == prev_length:
                counter += 1
            elif (self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'rsqaWe']")))[-1].text == 'a year ago') and (current_length >= self.min_length):
                keepScrolling = False
            self.max_scroll -= 1
            for i in self.driver.find_elements(By.XPATH, "//button[@class = 'w8nwRe kyuRq']"):
                i.click()
                time.sleep(0.8)
            
        review_id_list = self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//button[@class = 'al6Kxe']")))
        user_info_list = self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class = 'WNxzHc qLhwHc']")))
        user_href_list = self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//button[@class = 'al6Kxe']")))
        user_rating_list = self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'kvMYJc']")))
        reviews_list = self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class = 'GHT2ce']")))

        return review_id_list, user_info_list, user_href_list, user_rating_list, reviews_list

    def get_reviewid(self, review_id_raw):
        """
        Get the review id

        :param review_id_raw: web object containing review id
        """
        return review_id_raw.get_attribute('data-review-id')

    def get_text(self, text_raw):
        """
        Get text attribute

        :param text_raw: web object containing text attribute
        """
        return text_raw.text

    def get_userhref(self, user_href_raw):
        """
        Get the user href for each reviews

        :param user_href_raw: web object containing user href
        """
        return user_href_raw.get_attribute('data-href')

    def get_userrating(self, user_rating_raw):
        """
        Get the user ratings for each reviews

        :param user_rating_raw: web object containing review rating
        """
        return user_rating_raw.get_attribute('aria-label')
    
    def get_reviews(self):
        """
        Compile the information of the reviews into a Pandas DataFrame
        """
        review_id_list, user_info_list, user_href_list, user_rating_list, reviews_list = self.expand_reviews()
        review_id = list(map(self.get_reviewid, review_id_list))
        user_info = list(map(self.get_text, user_info_list))
        user_href = list(map(self.get_userhref, user_href_list))
        user_rating = list(map(self.get_userrating, user_rating_list))
        reviews_text = list(map(self.get_text, reviews_list))
        self.driver.close()
        
        reviews_sub = pd.DataFrame([review_id, user_info, user_href, user_rating, reviews_text]).transpose()
        reviews_sub.columns = ['review_id', 'user_info', 'user_href', 'rating', 'review']
        reviews_sub['restaurant_name'] = self.restaurant_name

        return reviews_sub
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import file_setup

class details():
    """
        Extract information about a restaurant from its Google Maps page

        param href (str): web link to the restaurant's Google Map page
        """
    def __init__(self, href):
        self.driver = file_setup.access_webpage(href)
        self.wait = WebDriverWait(self.driver, 30)

    def get_details(self):
        """
        Extract the following information of a restaurant
        - Type of Restaurant (e.g. Hawker Center, Bar)
        - Price level and label to get an indication of how expensive the restaurant is
        - Address
        - Restaurant's wensite if available
        """
        time.sleep(2)
        restaurant_type = self.wait.until(
                            EC.visibility_of_element_located(
                                (By.CSS_SELECTOR, "div.skqShb"))).text.split('\n')[-1]
        address = self.wait.until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "div.rogA2c "))).text
        price_label = ''
        price_level = ''
        website = ''
        try:
            price_label = self.driver.find_element(By.XPATH,
                                            "//span[@class = 'mgr77e']/span/span/span/span"
                                            ).get_attribute('aria-label')
            price_level = self.driver.find_element(By.XPATH,
                                            "//span[@class = 'mgr77e']/span/span/span/span"
                                            ).text
        except (TimeoutException, NoSuchElementException):
            pass

        try:
            website = self.driver.find_element(By.CSS_SELECTOR,
                                        "a.CsEnBe").get_attribute('href')
        except (TimeoutException, NoSuchElementException):
            pass

        return restaurant_type, price_label, price_level, address, website

    def get_latlong(self):
        """
        Get latitude and longitude of restaurant
        """
        str_error = ''
        try:
            element = self.wait.until(
                EC.visibility_of_element_located((By.XPATH,"//html/body")))
            ActionChains(self.driver).move_to_element(element).context_click().perform()
        except TimeoutException as str_error:
            pass

        if str_error:
            time.sleep(2)
            element = self.wait.until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.mLuXec")))
            lat_long = element.text
        else:
            pass

        str_error = ''
        try:
            element = self.wait.until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.mLuXec")))
            lat_long = element.text
        except TimeoutException as str_error:
            pass

        if str_error:
            time.sleep(2)
            element = self.wait.until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.mLuXec")))
            lat_long = element.text
        else:
            pass
        return lat_long

    def get_ophours(self):
        """
        Get operating hours of the restaurant
        """
        time.sleep(5)
        op_hours = ''
        to_error = False
        ne_error = False
        
        try:
            element = self.wait.until(
                        EC.visibility_of_element_located(
                            (By.XPATH,"//span[@aria-label = 'Show open hours for the week']")))
            element.click()
            time.sleep(3)
            op_hours = self.wait.until(
                        EC.visibility_of_all_elements_located(
                            (By.XPATH, "//table[@class = 'eK4R0e fontBodyMedium']")))[0].text
        except TimeoutException:
            to_error = True
            pass
        except NoSuchElementException:
            ne_error = True
            pass

        if to_error:
            try:
                element = self.wait.until(
                            EC.visibility_of_element_located(
                                (By.XPATH,"//span[@aria-label = 'Show open hours for the week']")))
                element.click()
                time.sleep(3)
            except TimeoutException:
                pass

        elif ne_error:
            try:
                element = self.wait.until(
                            EC.visibility_of_element_located(
                                (By.XPATH,"//button[contains(@aria-label, 'hours')]")))
                element.click()
                time.sleep(3)
                for i in self.driver.find_elements(By.XPATH, "//div[@aria-expanded='false']"):
                    i.click()
                op_hours = self.wait.until(
                            EC.visibility_of_all_elements_located(
                                (By.XPATH,
                                "//div[@class = 'm6QErb DxyBCb kA9KIf dS8AEf XiKgde ']")))[0].text
                element = self.driver.find_element(By.XPATH, "//button[@aria-label= 'Back']")
                element.click()

            except TimeoutException:
                to_error = True
                pass
            except NoSuchElementException:
                pass

            if to_error:
                element = self.wait.until(
                            EC.visibility_of_element_located(
                                (By.XPATH,"//button[contains(@aria-label, 'hours')]")))
                element.click()
                time.sleep(3)
                for i in self.driver.find_elements(By.XPATH, "//div[@aria-expanded='false']"):
                    i.click()
                op_hours = self.wait.until(
                            EC.visibility_of_all_elements_located(
                                (By.XPATH,
                                "//div[@class = 'm6QErb DxyBCb kA9KIf dS8AEf XiKgde ']")))[0].text
                element = self.driver.find_element(By.XPATH,"//button[@aria-label= 'Back']")
                element.click()

        return op_hours

    def get_poptime(self):
        """
        Get the restaurants' average popularity at different hours of each day from its Google Maps page
        """
        poptime = ''
        time.sleep(2)
        try:
            for i in range(7):
                element = self.wait.until(
                            EC.visibility_of_element_located(
                                (By.XPATH,
                                "//div[@class = 'goog-inline-block goog-menu-button-dropdown']")))
                element.click()
                element = self.wait.until(
                            EC.visibility_of_all_elements_located(
                                (By.XPATH, "//div[@class = 'goog-menuitem-content']")))[i]
                busy = element.text + ": "
                element.click()
                time.sleep(0.5)
                for j in self.wait.until(
                            EC.visibility_of_all_elements_located(
                                (By.XPATH, "//div[@class = 'g2BVhd eoFzo ']/div"))):
                    try:
                        busy += j.get_attribute('aria-label').replace("\u202f", "") + '; '
                    except (TimeoutException, NoSuchElementException, AttributeError):
                        busy += j.text + '; '
                poptime += busy
        except (TimeoutException, NoSuchElementException):
            pass
        return poptime

    def get_service(self):
        """
        Get services available at a restaurant
        """
        self.driver.refresh()
        time.sleep(5)
        service = ''
        ## Service Options
        try:
            element = self.wait.until(
                        EC.visibility_of_element_located(
                            (By.XPATH, "//div[contains(text(), 'About')]")))
            element.click()
            time.sleep(2)
            service_list = self.wait.until(
                            EC.visibility_of_all_elements_located(
                                (By.XPATH, "//div[@class='m6QErb DxyBCb kA9KIf dS8AEf XiKgde ']")))
            for i in service_list:
                service += i.text
            element = self.driver.find_element(By.XPATH, "//button[@aria-label= 'Back']")
            element.click()
        except (TimeoutException, NoSuchElementException):
            pass
        self.driver.close()
        return service
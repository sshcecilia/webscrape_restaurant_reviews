from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

def expand_reviews(driver, max_scroll = -1):
    element = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//button[@data-tab-index = '1']")))
    element.click()

    element = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Sort')]")))
    element.click()

    element = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[@data-index = '1']")))
    element.click()

    ## Scroll down 
    divSideBar = driver.find_element(By.CSS_SELECTOR,f"div[class='m6QErb DxyBCb kA9KIf dS8AEf ']")
    keepScrolling = True
    length = len(WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'rsqaWe']"))))

    while(keepScrolling):
        driver.execute_script('arguments[0].scrollTo(0, arguments[0].scrollHeight)', divSideBar)
        time.sleep(0.8)
        current_length = len(WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'rsqaWe']"))))
        if max_scroll == 0:
            keepScrolling = False
        elif current_length == length:
            keepScrolling = False
        elif (WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'rsqaWe']")))[-1].text == 'a year ago') and (current_length >= 300):
            keepScrolling = False
        max_scroll -= 1
        length = len(WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'rsqaWe']"))))
        for i in driver.find_elements(By.XPATH, "//button[@class = 'w8nwRe kyuRq']"):
            i.click()
            time.sleep(0.8)
        
    review_id_list = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, "//button[@class = 'al6Kxe']")))
    user_info_list = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class = 'WNxzHc qLhwHc']")))
    user_href_list = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, "//button[@class = 'al6Kxe']")))
    user_rating_list = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'kvMYJc']")))
    reviews_list = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class = 'GHT2ce']")))

    return review_id_list, user_info_list, user_href_list, user_rating_list, reviews_list

def get_reviewid(review_id_raw):
    return review_id_raw.get_attribute('data-review-id')

def get_text(text_raw):
    return text_raw.text

def get_userhref(user_href_raw):
    return user_href_raw.get_attribute('data-href')

def get_userrating(user_rating_raw):
    return user_rating_raw.get_attribute('aria-label')
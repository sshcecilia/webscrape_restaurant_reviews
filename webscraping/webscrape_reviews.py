from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

def get_info(driver):
    
    ## Type
    restaurant_type = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.skqShb"))).text.split('\n')[-1]

    ## Price Level
    price_label = ''
    price_level = ''

    try:
        price_label = driver.find_element(By.XPATH, "//span[@class = 'mgr77e']/span/span/span/span").get_attribute('aria-label')
        price_level = driver.find_element(By.XPATH, "//span[@class = 'mgr77e']/span/span/span/span").text
    except:
        pass
    
    ## Address
    address = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.rogA2c "))).text

    ## Website
    website = ''

    try:
        website = driver.find_element(By.CSS_SELECTOR, "a.CsEnBe").get_attribute('href')
    except:
        pass
    
    return restaurant_type, price_label, price_level, address, website

def get_latlong(driver):

    time.sleep(5)

    ## Get Lat Long 
    ActionChains(driver).move_to_element(WebDriverWait(driver, 25).until(EC.visibility_of_element_located((By.XPATH,"//html/body")))).context_click().perform()
    lat_long = str(WebDriverWait(driver, 25).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.mLuXec"))).text)

    return lat_long

def get_ophours(driver):

    op_hours = ''
    
    ## Operating hours
    try:
        time.sleep(5)
        element = driver.find_element(By.XPATH, "//span[@aria-label = 'Show open hours for the week']")
        element.click()

        for i in range(7):
            op_hours += WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//tr[@class = 'y0skZc']/td/div")))[i].text
            op_hours += ": "
            op_hours += WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//tr[@class = 'y0skZc']/td/ul/li")))[i].text.replace("\u202f", " ")
            op_hours += "; "
    except:
        pass

    return op_hours

def get_poptime(driver):

    poptime = list()

    ## Popular Times
    try:
        for i in range(7):
            element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@class = 'goog-inline-block goog-menu-button-dropdown']")))
            element.click()
            element = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class = 'goog-menuitem-content']")))[i]
            busy = element.text + ": "
            element.click()
            time.sleep(0.5)
            for j in WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class = 'g2BVhd eoFzo ']/div"))):
                try:
                    busy += j.get_attribute('aria-label').replace("\u202f", "") + '; '
                except:
                    busy += j.text + '; '     

            poptime.append(busy)

    except NoSuchElementException:
        pass
    except TimeoutException:
        pass

    return poptime

def get_service(driver):

    ## Service Options
    element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[@data-tab-index = '2']")))
    element.click()

    try:
        do = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//li[@class='hpLkke ']/span")))
    except:
        do = []

    try:
        dont = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//li[@class='hpLkke WeoVJe']/span")))
    except:
        dont = []

    services = ''
    for i in do:
        services += i.get_attribute('aria-label') + '; '

    for j in dont:
        services += j.get_attribute('aria-label') + '; '

    return services

def expand_reviews(driver, max_scroll = -1):
    element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[@data-tab-index = '1']")))
    element.click()

    element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Sort')]")))
    element.click()

    element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@data-index = '1']")))
    element.click()

    ## Scroll down 
    divSideBar = driver.find_element(By.CSS_SELECTOR,f"div[class='m6QErb DxyBCb kA9KIf dS8AEf ']")
    keepScrolling = True
    length = len(WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'rsqaWe']"))))

    while(keepScrolling):
        driver.execute_script('arguments[0].scrollTo(0, arguments[0].scrollHeight)', divSideBar)
        time.sleep(0.8)
        current_length = len(WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'rsqaWe']"))))
        if max_scroll == 0:
            keepScrolling = False
        elif current_length == length:
            keepScrolling = False
        elif (WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'rsqaWe']")))[-1].text == 'a year ago') and (current_length >= 300):
            keepScrolling = False
        max_scroll -= 1
        length = len(WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'rsqaWe']"))))
        for i in driver.find_elements(By.XPATH, "//button[@class = 'w8nwRe kyuRq']"):
            i.click()
            time.sleep(0.8)
        

    review_id_list = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//button[@class = 'al6Kxe']")))
    user_info_list = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class = 'WNxzHc qLhwHc']")))
    user_href_list = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//button[@class = 'al6Kxe']")))
    user_rating_list = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'kvMYJc']")))
    reviews_list = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class = 'GHT2ce']")))

    return review_id_list, user_info_list, user_href_list, user_rating_list, reviews_list

def get_reviewid(review_id_raw):
    return review_id_raw.get_attribute('data-review-id')

def get_text(text_raw):
    return text_raw.text

def get_userhref(user_href_raw):
    return user_href_raw.get_attribute('data-href')

def get_userrating(user_rating_raw):
    return user_rating_raw.get_attribute('aria-label')
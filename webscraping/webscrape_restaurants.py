from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

def access_webpage(url):
    """
    Open and return the driver to the url provided

    :param url: string object containing url of a website 
    """
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(300)
    driver.get(url)
    time.sleep(3)
    try:
        driver.maximize_window()
    except:
        pass
    
    return driver

def search_scroll(driver, query, max_scroll = -1):
    """
    Search based on the query provided and scroll down the website to get the full list of restaurants

    :param driver: webdriver object
    :param query: keyword to enter into the searchbox
    :param max_scroll: int containing the number of times to scroll. default is -1 to scroll until the end of the page.
    """
    wait = WebDriverWait(driver, 30)
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
        if ((html.find("You've reached the end of the list.") != -1) | max_scroll == 0):
            keepScrolling = False
        max_scroll -= 1

def restaurant_list(driver):
    """
    Obtain a list of elements for the restaurants extracted from the webpage
    
    :param driver: webdriver object
    """
    raw = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
    return raw

def get_basic(element):
    """
    Extract the following information of a restaurant
    - Name of the restaurants
    - Google maps link of the restaurant
    - Status of the restaurant (whether the store is operating)
    - Ratings and Number of reviews

    :param element: An element of a webpage
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

def get_details(driver):
    """
    Extract additional information of a restaurant from its Google Maps page
    - Type of Restaurant (e.g. Hawker Center, Bar)
    - Price level and label to get an indication of how expensive the restaurant is
    - Address
    - Restaurant's wensite if available

    param driver: webdriver object
    """
    time.sleep(2)
    restaurant_type = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.skqShb"))).text.split('\n')[-1]
    address = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.rogA2c "))).text
    price_label = ''
    price_level = ''
    website = ''

    try:
        price_label = driver.find_element(By.XPATH, "//span[@class = 'mgr77e']/span/span/span/span").get_attribute('aria-label')
        price_level = driver.find_element(By.XPATH, "//span[@class = 'mgr77e']/span/span/span/span").text
    except (TimeoutException, NoSuchElementException):
        pass

    try:
        website = driver.find_element(By.CSS_SELECTOR, "a.CsEnBe").get_attribute('href')
    except (TimeoutException, NoSuchElementException):
        pass
    
    return restaurant_type, price_label, price_level, address, website

def get_latlong(driver):
    """
    Get latitude and longitude of restaurant

    param driver: webdriver object
    """
    str_error = ''
    try:
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH,"//html/body")))
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH,"//html/body")))
        ActionChains(driver).move_to_element(element).context_click().perform()
    except TimeoutException as str_error:
        pass   
    if str_error:
        time.sleep(2)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.mLuXec")))
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.mLuXec")))

        lat_long = element.text
    else:
        pass
    
    str_error = ''
    try:
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.mLuXec")))
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.mLuXec")))
        lat_long = element.text
    except TimeoutException as str_error:
        pass 
    if str_error:
        time.sleep(2)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.mLuXec")))
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.mLuXec")))

        lat_long = element.text
    else:
        pass

    return lat_long

def get_ophours(driver):
    """
    Get operating hours of the restaurant

    param driver: webdriver object
    """
    time.sleep(5)
    op_hours = ''
    to_error = ''
    ne_error = ''
    
    try:
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH,"//span[@aria-label = 'Show open hours for the week']")))
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH,"//span[@aria-label = 'Show open hours for the week']")))
        element.click()
        time.sleep(3)

        op_hours = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, "//table[@class = 'eK4R0e fontBodyMedium']")))[0].text

    except TimeoutException as to_error:
        pass
    
    except NoSuchElementException as ne_error:
        pass

    if to_error:
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH,"//span[@aria-label = 'Show open hours for the week']")))
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH,"//span[@aria-label = 'Show open hours for the week']")))
        element.click()
        time.sleep(3)

    elif ne_error:
        try:
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH,"//button[contains(@aria-label, 'hours')]")))
            element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH,"//button[contains(@aria-label, 'hours')]")))
            element.click()
            time.sleep(3)

            for i in driver.find_elements(By.XPATH, "//div[@aria-expanded='false']"):
                i.click()
            op_hours = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class = 'm6QErb DxyBCb kA9KIf dS8AEf XiKgde ']")))[0].text
            element = driver.find_element(By.XPATH, "//button[@aria-label= 'Back']")
            element.click()

        except TimeoutException as to_error:
            pass
        
        except NoSuchElementException:
            pass

        if to_error:
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH,"//button[contains(@aria-label, 'hours')]")))
            element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH,"//button[contains(@aria-label, 'hours')]")))
            element.click()
            time.sleep(3)

            for i in driver.find_elements(By.XPATH, "//div[@aria-expanded='false']"):
                i.click()
            op_hours = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class = 'm6QErb DxyBCb kA9KIf dS8AEf XiKgde ']")))[0].text
            element = driver.find_element(By.XPATH, "//button[@aria-label= 'Back']")
            element.click()

    return op_hours

def get_poptime(driver):
    """
    Get popular times based on Google Maps

    param driver: webdriver object
    """

    poptime = ''
    time.sleep(2)

    try:
        for i in range(7):
            element = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[@class = 'goog-inline-block goog-menu-button-dropdown']")))
            element.click()
            element = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class = 'goog-menuitem-content']")))[i]
            busy = element.text + ": "
            element.click()
            time.sleep(0.5)
            for j in WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class = 'g2BVhd eoFzo ']/div"))):
                try:
                    busy += j.get_attribute('aria-label').replace("\u202f", "") + '; '
                except:
                    busy += j.text + '; '     

            poptime += busy

    except (TimeoutException, NoSuchElementException):
        pass

    return poptime

def get_service(driver):
    """
    Get services available at a restaurant

    param driver: webdriver object
    """

    time.sleep(5)
    service = ''

    ## Service Options
    try:
        element = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(), 'About')]")))
        element.click()
        time.sleep(2)

        service_list = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class='m6QErb DxyBCb kA9KIf dS8AEf XiKgde ']")))
        for i in service_list:
            service += i.text
        element = driver.find_element(By.XPATH, "//button[@aria-label= 'Back']")
        element.click()
    except (TimeoutException, NoSuchElementException):
        pass
    return service
import webscrape_restaurants
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import re
import time
import pandas as pd



def extract_info(driver):
    wait = WebDriverWait(driver, 10)
    
    ## Type
    type = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.skqShb"))).text.split('\n')[-1]

    ## Price Level
    try:
        price_label = driver.find_element(By.XPATH, "//span[@class = 'mgr77e']/span/span/span/span").get_attribute('aria-label')
        price_level = driver.find_element(By.XPATH, "//span[@class = 'mgr77e']/span/span/span/span").text
    except:
        pass
    
    ## Address
    time.sleep(1)
    address = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.rogA2c "))).text

    ## Website
    try:
        website = driver.find_element(By.CSS_SELECTOR, "a.CsEnBe").get_attribute('href')
    except:
        pass

    ## Get Lat Long 
    time.sleep(1)
    ActionChains(driver).move_to_element(wait.until(EC.visibility_of_element_located((By.XPATH,"//html/body")))).context_click().perform()
    links.at[row, 'lat_long'] = str(wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.mLuXec"))).text)

    ## Ratings
    #links.at[row, 'ratings'] = float(wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.F7nice"))).text[:re.search('\n', driver.find_elements(By.CSS_SELECTOR, "div.F7nice")[0].text).span()[0]])
    #links.at[row, 'num_reviews'] = int(wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.F7nice"))).text[re.search('\n', driver.find_elements(By.CSS_SELECTOR, "div.F7nice")[0].text).span()[1]+1:-1])
    
    ## Operating hours
    try:
        element = driver.find_element(By.XPATH, "//span[@aria-label = 'Show open hours for the week']")
        element.click()

        op_hours = ''
        for i in range(7):
            op_hours += wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//tr[@class = 'y0skZc']/td/div")))[i].text
            op_hours += ": "
            op_hours += wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//tr[@class = 'y0skZc']/td/ul/li")))[i].text.replace("\u202f", " ")
            op_hours += "; "
        links.at[row, 'op_hours'] = op_hours
    except:
        pass

    ## Popular Times

    try:
        col = [j for j in links.columns if j.startswith('popular')]
        for i in range(7):
            element = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class = 'goog-inline-block goog-menu-button-dropdown']")))
            element.click()
            element = wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class = 'goog-menuitem-content']")))[i]
            busy = element.text + ": "
            element.click()
            time.sleep(0.5)
            for j in wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class = 'g2BVhd eoFzo ']/div"))):
                try:
                    busy += j.get_attribute('aria-label').replace("\u202f", "") + '; '
                except:
                    busy += j.text + '; '     

            links.at[row, col[i]] = busy
    except NoSuchElementException:
        pass
    except TimeoutException:
        pass

    ## Service Options
    element = wait.until(EC.visibility_of_element_located((By.XPATH, "//button[@data-tab-index = '2']")))
    element.click()

    try:
        do = wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//li[@class='hpLkke ']/span")))
    except:
        do = []

    try:
        dont = wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//li[@class='hpLkke WeoVJe']/span")))
    except:
        dont = []

    services = ''
    for i in do:
        services += i.get_attribute('aria-label') + '; '

    for j in dont:
        services += j.get_attribute('aria-label') + '; '

    links.at[row, 'services'] = services

    ## Extract Reviews

    element = wait.until(EC.visibility_of_element_located((By.XPATH, "//button[@data-tab-index = '1']")))
    element.click()

    element = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Sort')]")))
    element.click()

    element = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@data-index = '1']")))
    element.click()

    ## Scroll down 
    divSideBar = driver.find_element(By.CSS_SELECTOR,f"div[class='m6QErb DxyBCb kA9KIf dS8AEf ']")
    keepScrolling = True
    length = len(wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'rsqaWe']"))))

    while(keepScrolling):
        driver.execute_script('arguments[0].scrollTo(0, arguments[0].scrollHeight)', divSideBar)
        time.sleep(0.8)
        current_length = len(wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'rsqaWe']"))))
        if current_length == length:
            keepScrolling = False
        elif (wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'rsqaWe']")))[-1].text == 'a year ago') and (current_length >= 300):
            keepScrolling = False
        length = len(wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'rsqaWe']"))))
        for i in driver.find_elements(By.XPATH, "//button[@class = 'w8nwRe kyuRq']"):
            i.click()
            time.sleep(0.8)

    review_subset = pd.DataFrame()

    review_subset['id'] = links.loc[row, 'id']
    review_subset['data-review-id'] = list(map(lambda x: x.get_attribute('data-review-id'), wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//button[@class = 'al6Kxe']")))))
    review_subset['user_info'] = list(map(lambda x: x.text, wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class = 'WNxzHc qLhwHc']")))))
    review_subset['user_href'] = list(map(lambda x: x.get_attribute('data-href'), wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//button[@class = 'al6Kxe']")))))
    review_subset['user_rating'] = list(map(lambda x: x.get_attribute('aria-label'), wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class = 'kvMYJc']")))))
    review_subset['entries'] = list(map(lambda x: x.text, wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class = 'GHT2ce']")))))

    reviews.append(review_subset, ignore_index = True)
    reviews.to_csv('C:/Users/csoh/OneDrive - Revenue Management Solutions, LLC/Desktop/NUS/DSA5201/reviews.csv', index = False)
    links.loc[row, 'Done'] = 1
    links.to_csv('C:/Users/csoh/OneDrive - Revenue Management Solutions, LLC/Desktop/NUS/DSA5201/links.csv', index = False)

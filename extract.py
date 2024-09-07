from webscrape_restaurants import access_webpage, search_scroll, restaurant_list, extract_basic

driver = access_webpage(url = "https://www.google.com/maps")
search_scroll(driver, "Food in Singapore", 2)
raw = restaurant_list(driver)


test = map(extract_basic, raw)
import pandas as pd
pd.DataFrame(test, columns = ['name', 'href', 'status', 'info'])

type(raw)

driver.close()

data




data = pd.DataFrame(columns = ['name', 'href', 'status', 'info'])
    raw = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")

    for i in range(len(raw)):

        # Skip extracting restaurant if link has been scraped. Avoid duplicate copies of the same restaurant.
        if sum(data['href'].isin([raw[i].find_elements(By.CSS_SELECTOR, "a.hfpxzc")[0].get_attribute('href')])) >= 1: 
            continue

        # If Status is not available, set it to 'Open'. If number of reviews are not available
        elif (len(raw[i].find_elements(By.CSS_SELECTOR, "span.eXlrNe")) == 0):
            name = raw[i].find_elements(By.CSS_SELECTOR, "a.hfpxzc")[0].get_attribute('aria-label')
            href = [raw[i].find_elements(By.CSS_SELECTOR, "a.hfpxzc")[0].get_attribute('href')]
            status = ['Open']
            info = [raw[i].find_elements(By.CSS_SELECTOR, "span.ZkP5Je")[0].get_attribute('aria-label')]

            data = pd.concat([data, pd.DataFrame({'name': name, 'href': href, 'status': status, 'info': info})], ignore_index = True)

        else:
            name = raw[i].find_elements(By.CSS_SELECTOR, "a.hfpxzc")[0].get_attribute('aria-label')
            href = [raw[i].find_elements(By.CSS_SELECTOR, "a.hfpxzc")[0].get_attribute('href')]
            status = [raw[i].find_elements(By.CSS_SELECTOR, "span.eXlrNe")[0].text]
            info = [raw[i].find_elements(By.CSS_SELECTOR, "span.ZkP5Je")[0].get_attribute('aria-label')]

            data = pd.concat([data, pd.DataFrame({'name': name, 'href': href, 'status': status, 'info': info})], ignore_index = True) 

    return data
from webscraping import webscrape_restaurants
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, datetime
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import os

def access_webpage(url):
    """
    Open and return the driver to the url provided

    :param url (str): url of a website 
    """
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(300)
    driver.get(url)
    time.sleep(3)
    try:
        driver.maximize_window()
    except (TimeoutException, NoSuchElementException):
        pass
    return driver

def get_streetname(driver):
    """
    Extract the list of streetname from the website

    :param driver: driver object of the website
    """
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'li')))   
    raw = driver.find_elements(By.CSS_SELECTOR, "li")
    street = map(lambda x: x.text, raw)
    return street

def combine_data(main_file, sub_file, merge_on, update_col = []):
    """
    Update the columns listed in update_col from the sub_file to the main_file and concatenate two files and remove duplicated entries if any
    If update_col is an empty list, to concatenate two files and remove duplicated entries
    Return the combined file as output

    :param main_file (pandas DataFrame): DataFrame containing the main file to be updated and stored
    :param sub_file (pandas DataFrame): DataFrame containing the sub file containing the data to be updated to the main file
    :param merge_on (list): List containing the column names common to the main and sub file to merge the two dataframe
    :param update_col (list): List containing the column names common to the main and sub file to be updated
    """
    combined_file = main_file.copy()
    if (type(merge_on) != list) or (type(update_col) != list):
        raise Exception("Provide variable name as a list")
    compare_file = main_file.merge(sub_file, on = merge_on, how = 'left')
    for i in update_col:
        combined_file.loc[(compare_file[i + '_x'] != compare_file[i + '_y']) & (compare_file[i + '_y'].isnull() == False), i] = compare_file.loc[(compare_file[i + '_x'] != compare_file[i + '_y']) & (compare_file[i + '_y'].isnull() == False), i + '_y']            
    combined_file = pd.concat([combined_file, sub_file], join = 'outer', sort = False, ignore_index = True)
    combined_file.drop_duplicates(subset = merge_on, keep = 'first', inplace = True, ignore_index = True)
    return combined_file

def compile_data(restaurant_dir, review_dir, streetname_dir):
    """
    Should duplicated restaurants, reviews and streetname files exists in the folder, to combine them into one file and remove the remaining
    Returns the restaurants, reviews and streetname data as output

    :param restaurant_dir (str): directory to get or store the restaurants data
    :param review_dir (str): directory to get or store the reviews data
    :param streetname_dir (str): directory to get or store the streetname data
    """
    restaurants = pd.read_csv(restaurant_dir, keep_default_na=False)
    streetname = pd.read_csv(streetname_dir, keep_default_na=False)
    reviews = pd.read_csv(review_dir, keep_default_na=False)

    index = [i for i in range(len(restaurant_dir)) if restaurant_dir.startswith('/', i)]

    if len(index) > 0:
        folder =  './' + restaurant_dir[:index[-1]] +'/'
        restaurants_filename = restaurant_dir[index[-1]+1:restaurant_dir.find('.csv')] + '_'
        streetname_filename = streetname_dir[index[-1]+1:streetname_dir.find('.csv')] + '_'
        reviews_filename = review_dir[index[-1]+1:review_dir.find('.csv')] + '_'
    else :
        folder = './'
        restaurants_filename = restaurant_dir[:restaurant_dir.find('.csv')] + '_'
        streetname_filename = streetname_dir[:streetname_dir.find('.csv')] + '_'
        reviews_filename = review_dir[:review_dir.find('.csv')] + '_'

    for i in os.listdir(folder):
        if restaurants_filename in i:
            restaurants_subset = pd.read_csv(folder + i)
            merged_file = restaurants.merge(restaurants_subset, on = ['restaurant_name', 'href'], how = 'right')
            restaurants_subset_update = restaurants_subset[merged_file['overview_last_updated_y'].apply(lambda x: datetime.now() if pd.isna(x) else datetime.strptime(x, '%Y-%m-%d')) > merged_file['overview_last_updated_x'].apply(lambda x: datetime.now() if pd.isna(x) else datetime.strptime(x, '%Y-%m-%d'))]
            restaurants = combine_data(restaurants, restaurants_subset_update, merge_on = ['restaurant_name', 'href'], update_col = ['status', 'info','overview_last_updated'])
            restaurants_subset_update = restaurants_subset[merged_file['details_last_updated_y'].apply(lambda x: datetime.now() if pd.isna(x) else datetime.strptime(x, '%Y-%m-%d')) > merged_file['details_last_updated_x'].apply(lambda x: datetime.now() if pd.isna(x) else datetime.strptime(x, '%Y-%m-%d'))]
            restaurants = combine_data(restaurants, restaurants_subset_update, merge_on = ['restaurant_name', 'href'], update_col = ['type', 'price_label','price_level','address','website','lat_long','op_hours','poptime','services','details_last_updated'])
            restaurants_subset_update = restaurants_subset[merged_file['reviews_last_updated_y'].apply(lambda x: datetime.now() if pd.isna(x) else datetime.strptime(x, '%Y-%m-%d')) > merged_file['reviews_last_updated_x'].apply(lambda x: datetime.now() if pd.isna(x) else datetime.strptime(x, '%Y-%m-%d'))]
            restaurants = combine_data(restaurants, restaurants_subset_update, merge_on = ['restaurant_name', 'href'], update_col = ['reviews_last_updated'])
            restaurants = combine_data(restaurants, restaurants_subset, merge_on = ['restaurant_name', 'href'], update_col = [])
            restaurants.to_csv(restaurant_dir, index = False)
            os.remove(folder + i)
        elif streetname_filename in i:
            streetname_subset = pd.read_csv(folder + i)
            streetname = combine_data(streetname, streetname_subset, merge_on = ['street'], update_col = ['last_updated'])
            streetname.to_csv(streetname_dir, index = False)
            os.remove(folder + i)
        elif reviews_filename in i:
            reviews_subset = pd.read_csv(folder + i)
            reviews = combine_data(reviews, reviews_subset, merge_on = ['restaurant_name', 'review_id', 'user_href'], update_col = [])
            reviews.to_csv(review_dir, index = False)
            os.remove(folder + i)
    
    return restaurants, reviews, streetname 

def initial_setup(restaurant_dir, review_dir, streetname_dir, initial):
    """
    Set up the necessary files to store the extracted information and the files are returned as Pandas DataFrame

    :param restaurant_dir (str): directory to get or store the restaurants data
    :param review_dir (str): directory to get or store the reviews data
    :param streetname_dir (str): directory to get or store the streetname data
    :param initial (boolean):   whether it is the first file setup
                                if yes, create the file, else access the files
    """
    if initial == False:
        restaurants, reviews, streetname = compile_data(restaurant_dir, review_dir, streetname_dir)

    else:
        ## Creation of DataFrame to Store Restaurant Information
        restaurants = pd.DataFrame({'restaurant_name': pd.Series(dtype='str'),
                                    'href': pd.Series(dtype='str'),
                                    'status': pd.Series(dtype='str'),
                                    'info': pd.Series(dtype='str'),
                                    'type': pd.Series(dtype='str'),
                                    'price_label': pd.Series(dtype='str'),
                                    'price_level': pd.Series(dtype='str'),
                                    'address': pd.Series(dtype='str'),
                                    'website': pd.Series(dtype='str'),
                                    'lat_long': pd.Series(dtype='str'),
                                    'op_hours': pd.Series(dtype='str'),
                                    'poptime': pd.Series(dtype='str'),
                                    'services': pd.Series(dtype='str'),
                                    'overview_last_updated': pd.Series(dtype='str'),
                                    'details_last_updated': pd.Series(dtype='str'),
                                    'reviews_last_updated': pd.Series(dtype='str')})
        
        reviews = pd.DataFrame({'restaurant_name': pd.Series(dtype='str'),
                                'review_id': pd.Series(dtype='str'),
                                'user_info': pd.Series(dtype='str'),
                                'user_href': pd.Series(dtype='str'),
                                'rating': pd.Series(dtype='str'),
                                'review': pd.Series(dtype='str')})

        ## Extraction of List of Streetname in Singapore
        driver = access_webpage(url = "https://geographic.org/streetview/singapore/index.html")
        streetname = pd.DataFrame(['Singapore'], columns = ['street'])
        streetname = pd.concat([streetname, pd.DataFrame(get_streetname(driver), columns = ['street'])], sort = False, ignore_index = True)
        streetname.drop_duplicates(inplace = True)
        streetname[['last_updated']] = date(1900,1,1)
        driver.close()

        restaurants.to_csv(restaurant_dir, index = False)
        reviews.to_csv(review_dir, index = False)
        streetname.to_csv(streetname_dir, index = False)

    return restaurants, reviews, streetname
    
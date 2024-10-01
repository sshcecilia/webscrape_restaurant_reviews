from webscraping import file_setup
from webscraping import webscrape_restaurants
from webscraping import webscrape_details
from webscraping import webscrape_reviews
from datetime import date, datetime
import pandas as pd
import threading

class refresh_data():
    """
    Refresh restaurants and reviews data

    :param restaurant_dir (str): directory to get or store the restaurants data
    :param review_dir (str): directory to get or store the reviews data
    :param streetname_dir (str): directory to get or store the streetname data
    :param initial (boolean):   whether it is the first file setup
                                if yes, create the file, else access the files
    """
    def __init__(self, restaurant_dir, review_dir, streetname_dir, initial = False):
        self.restaurant_dir = restaurant_dir
        self.review_dir = review_dir
        self.streetname_dir = streetname_dir
        self.initial = initial
        self.restaurants, self.reviews, self.streetname = file_setup.initial_setup(restaurant_dir,
                                                                review_dir,
                                                                streetname_dir,
                                                                initial)
        
    def days_since(self, input_date):
        """
        Calculate the number of days between the input date and today

        :param input_date (str or date): date to be calculated
        """
        if type(input_date) == str:
            input_date =  datetime.strptime(input_date, '%Y-%m-%d').date()
        elif type(input_date) == pd.Timestamp:
            input_date = input_date.date()
        return (date.today() - input_date).days

    def refresh_restaurants(self, restaurant_update_freq = 30, max_scroll = -1, max_tries = 5):
        """
        Refresh the list of restaurants

        :param restaurant_update_freq (int): interval to update the list of restaurants
        :param max_scroll (int): the number of times to scroll
                             default value is -1 which will scroll till the end of the page
        :param max_tries (int): the number of times to retry scrolling the webpage should the webpage takes too long to load
                            default value is 5
        """
        for i in self.streetname[self.streetname['last_updated'].apply(self.days_since) >= restaurant_update_freq].index:
            restaurant_list = webscrape_restaurants.restaurants(self.streetname.loc[i, 'street'], max_scroll, max_tries)
            restaurants_subset = restaurant_list.get_restaurant()
            if isinstance(restaurants_subset, pd.DataFrame) :
                self.restaurants = pd.concat([self.restaurants, restaurants_subset], join = 'outer', sort = False, ignore_index = True)
                self.restaurants.drop_duplicates(subset = ['restaurant_name', 'href'], keep = 'first', inplace = True, ignore_index = True)
                self.restaurants.to_csv(self.restaurant_dir, index = False)
                self.streetname.loc[i, 'last_updated'] = date.today()
                self.streetname.to_csv(self.streetname_dir, index = False)

    def refresh_details(self, details_update_freq = 30):
        """
        Refresh the details of a restaurant

        :param details_update_freq (int): interval to update the details of a restaurant
        """
        for i in self.restaurants[self.restaurants['details_last_updated'].apply(self.days_since) >= details_update_freq].index:
            restaurant_details = webscrape_details.details(self.restaurants['href'].iloc[i])
            self.restaurants.loc[i,'type'], self.restaurants.loc[i,'price_label'], self.restaurants.loc[i,'price_level'], self.restaurants.loc[i,'address'], self.restaurants.loc[i,'website'] = restaurant_details.get_details()
            self.restaurants.loc[i,'lat_long'] = restaurant_details.get_latlong()
            self.restaurants.loc[i,'op_hours'] = restaurant_details.get_ophours()
            self.restaurants.loc[i,'poptime'] = restaurant_details.get_poptime()
            self.restaurants.loc[i,'services'] = restaurant_details.get_service()
            self.restaurants.loc[i,'details_last_updated'] = date.today()
            self.restaurants.to_csv(self.restaurant_dir, index = False)

    def refresh_reviews(self, reviews_update_freq = 30, max_scroll = -1, max_tries = 5, min_length = 300):
        """
        Refresh the reviews of a restaurant

        :param reviews_update_freq (int): interval to update the restaurant's reviews
        :param max_scroll (int): the number of times to scroll
                             default value is -1 which will scroll till the end of the page
        :param max_tries (int): the number of times to retry scrolling the webpage should the webpage takes too long to load
                                default value is 5
        :param min_length (int): Ooly extract customer's reviews within a year or at least min_length number of reviews whichever larger
                                default value is 300
        """
        type_to_exclude = ['Interior designer','Park·\ue934','Historical landmark·\ue934','Corporate office']
        for i in self.restaurants[(self.restaurants['reviews_last_updated'].apply(self.days_since) >= reviews_update_freq) & (self.restaurants['status'] == "Open") & (~self.restaurants['type'].isin(type_to_exclude))].index:
            reviews_list = webscrape_reviews.reviews(self.restaurants['href'].iloc[i], self.restaurants['restaurant_name'].iloc[i], max_scroll, max_tries, min_length)
            reviews_sub = reviews_list.get_reviews()
            self.reviews = pd.concat([self.reviews,reviews_sub], sort = False, ignore_index = True)
            self.reviews.drop_duplicates(subset = ['restaurant_name', 'review_id', 'user_href'], keep = 'first', inplace = True, ignore_index = True)
            self.reviews.to_csv(self.review_dir, index = False)
            self.restaurants.loc[i, 'reviews_last_updated'] = date.today()
            self.restaurants.to_csv(self.restaurant_dir, index = False)

class parallel_refresh_data():

    def __init__(self, restaurant_dir, review_dir, streetname_dir, initial = False):
        self.initial = initial
        self.restaurant_dir = restaurant_dir
        self.review_dir = review_dir
        self.streetname_dir = streetname_dir
        self.restaurants, self.reviews, self.streetname = file_setup.initial_setup(restaurant_dir,
                                                                review_dir,
                                                                streetname_dir,
                                                                initial)

    def refresh_restaurants_fn(self, restaurant_sub_dir, review_sub_dir, streetname_sub_dir, initial = False, restaurant_update_freq = 30, max_scroll = -1, max_tries = 5):
        """
        Instantiate the refresh_data class and run the refresh_restaurants function

        :param restaurant_sub_dir (str): directory to get or store the restaurants data
        :param review_sub_dir (str): directory to get or store the reviews data
        :param streetname_sub_dir (str): directory to get or store the streetname data
        :param initial (boolean):   whether it is the first file setup
                                    if yes, create the file, else access the files
        :param restaurant_update_freq (int): interval to update the list of restaurants
        :param max_scroll (int): the number of times to scroll
                             default value is -1 which will scroll till the end of the page
        :param max_tries (int): the number of times to retry scrolling the webpage should the webpage takes too long to load
                            default value is 5
        """
        sub_data = refresh_data(restaurant_sub_dir, review_sub_dir, streetname_sub_dir, initial)
        sub_data.refresh_restaurants(restaurant_update_freq, max_scroll, max_tries)

    def refresh_details_fn(self, restaurant_sub_dir, review_sub_dir, streetname_sub_dir, initial = False, details_update_freq = 30):
        """
        Instantiate the refresh_data class and run the refresh_details function

        :param restaurant_sub_dir (str): directory to get or store the restaurants data
        :param review_sub_dir (str): directory to get or store the reviews data
        :param streetname_sub_dir (str): directory to get or store the streetname data
        :param initial (boolean):   whether it is the first file setup
                                    if yes, create the file, else access the files
        :param details_update_freq (int): interval to update the details of a restaurant
        """
        sub_data = refresh_data(restaurant_sub_dir, review_sub_dir, streetname_sub_dir, initial)
        sub_data.refresh_details(details_update_freq)

    def refresh_reviews_fn(self, restaurant_sub_dir, review_sub_dir, streetname_sub_dir, initial = False, reviews_update_freq = 30, max_scroll = -1, max_tries = 5, min_length = 300):
        """
        Instantiate the refresh_data class and run the refresh_reviews function

        :param restaurant_sub_dir (str): directory to get or store the restaurants data
        :param review_sub_dir (str): directory to get or store the reviews data
        :param streetname_sub_dir (str): directory to get or store the streetname data
        :param initial (boolean):   whether it is the first file setup
                                    if yes, create the file, else access the files
        :param reviews_update_freq (int): interval to update the restaurant's reviews
        :param max_scroll (int): the number of times to scroll
                             default value is -1 which will scroll till the end of the page
        :param max_tries (int): the number of times to retry scrolling the webpage should the webpage takes too long to load
                                default value is 5
        :param min_length (int): Ooly extract customer's reviews within a year or at least min_length number of reviews whichever larger
                                default value is 300
        """
        sub_data = refresh_data(restaurant_sub_dir, review_sub_dir, streetname_sub_dir, initial)
        sub_data.refresh_reviews(reviews_update_freq, max_scroll, max_tries, min_length)

    def parallel_refresh_restaurants(self, num_threads = 1, restaurant_update_freq = 30, max_scroll = -1, max_tries = 5):
        """
        Parallel processing of the refresh_restaurants function

        :param num_threads (int): number of threads to run function in parallel
        :param max_scroll (int): the number of times to scroll
                             default value is -1 which will scroll till the end of the page
        :param max_tries (int): the number of times to retry scrolling the webpage should the webpage takes too long to load
                            default value is 5
        """    
        breakpt = list(range(0, self.streetname.shape[0], int(self.streetname.shape[0]/num_threads)))
        threads = []

        for i in range(num_threads):
            new_streetname_dir = self.streetname_dir[:self.streetname_dir.find('.csv')] + f'_{i}.csv'
            new_restaurant_dir = self.restaurant_dir[:self.restaurant_dir.find('.csv')] + f'_{i}.csv'
            if i == num_threads - 1:
                self.streetname.iloc[breakpt[i]:].to_csv(new_streetname_dir, index = False)
            else:
                self.streetname.iloc[breakpt[i]:breakpt[i+1]].to_csv(new_streetname_dir, index = False)           
            pd.DataFrame().reindex_like(self.restaurants).dropna().to_csv(new_restaurant_dir, index = False)

            t = threading.Thread(target = self.refresh_restaurants_fn, args = (new_restaurant_dir, self.review_dir, new_streetname_dir, False, restaurant_update_freq, max_scroll, max_tries))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        self.restaurants, self.reviews, self.streetname = file_setup.compile_data(self.restaurant_dir, self.review_dir, self.streetname_dir)

    def parallel_refresh_details(self, num_threads = 1, details_update_freq = 30):
        """
        Parallel processing of the refresh_details function

        :param num_threads (int): number of threads to run function in parallel
        :param details_update_freq (int): interval to update the details of a restaurant
        """
        breakpt = list(range(0, self.restaurants.shape[0], int(self.restaurants.shape[0]/num_threads)))
        threads = []

        for i in range(num_threads):
            new_restaurant_dir = self.restaurant_dir[:self.restaurant_dir.find('.csv')] + f'_{i}.csv'
            if i == num_threads - 1:
                self.restaurants.iloc[breakpt[i]:].to_csv(new_restaurant_dir, index = False)
            else:
                self.restaurants.iloc[breakpt[i]:breakpt[i+1]].to_csv(new_restaurant_dir, index = False)

            t = threading.Thread(target = self.refresh_details_fn, args = (new_restaurant_dir, self.review_dir, self.streetname_dir, False, details_update_freq))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        self.restaurants, self.reviews, self.streetname = file_setup.compile_data(self.restaurant_dir, self.review_dir, self.streetname_dir) 

    def parallel_refresh_reviews(self, num_threads = 1, reviews_update_freq = 30, max_scroll = -1, max_tries = 5, min_length = 300):
        """
        Parallel processing of the refresh_reviews function

        :param num_threads (int): number of threads to run function in parallel
        :param max_scroll (int): the number of times to scroll
                             default value is -1 which will scroll till the end of the page
        :param max_tries (int): the number of times to retry scrolling the webpage should the webpage takes too long to load
                                default value is 5
        :param min_length (int): Ooly extract customer's reviews within a year or at least min_length number of reviews whichever larger
                                default value is 300
        """
        breakpt = list(range(0, self.restaurants.shape[0], int(self.restaurants.shape[0]/num_threads)))
        threads = []

        for i in range(num_threads):
            new_restaurant_dir = self.restaurant_dir[:self.restaurant_dir.find('.csv')] + f'_{i}.csv'
            new_review_dir = self.review_dir[:self.review_dir.find('.csv')] + f'_{i}.csv'
            if i == num_threads - 1:
                self.restaurants.iloc[breakpt[i]:].to_csv(new_restaurant_dir, index = False)
            else:
                self.restaurants.iloc[breakpt[i]:breakpt[i+1]].to_csv(new_restaurant_dir, index = False)
            pd.DataFrame().reindex_like(self.reviews).dropna().to_csv(new_review_dir, index = False)

            t = threading.Thread(target = self.refresh_reviews_fn, args = (new_restaurant_dir, new_review_dir, self.streetname_dir, False, reviews_update_freq, max_scroll, max_tries, min_length))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        self.restaurants, self.reviews, self.streetname = file_setup.compile_data(self.restaurant_dir, self.review_dir, self.streetname_dir)
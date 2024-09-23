import file_setup
import webscrape_restaurants
import webscrape_details
import webscrape_reviews
from datetime import date, datetime
import pandas as pd

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
        self.initial = initial
        self.restaurant_dir = restaurant_dir
        self.review_dir = review_dir
        self.streetname_dir = streetname_dir
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
        return (date.today() - input_date).days

    def refresh_restaurants(self, restaurant_update_freq = 30):
        """
        Refresh the list of restaurants

        :param restaurant_update_freq (int): interval to update the list of restaurants
        """
        for i in self.streetname[self.streetname['last_updated'].apply(self.days_since) >= restaurant_update_freq].index:
            restaurant_list = webscrape_restaurants.restaurants(self.streetname.loc[i, 'street'])
            restaurants_subset = restaurant_list.get_restaurant()
            if isinstance(restaurants_subset, pd.DataFrame) :
                self.restaurants = pd.concat([self.restaurants, restaurants_subset], join = 'outer', sort = False, ignore_index = True)
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
            
    def refresh_reviews(self, reviews_update_freq = 30):
        """
        Refresh the reviews of a restaurant

        :param reviews_update_freq (int): interval to update the restaurant's reviews
        """
        for i in self.restaurants[self.restaurants['reviews_last_updated'].apply(self.days_since) >= reviews_update_freq].index:
            reviews_list = webscrape_reviews.reviews(self.restaurants['href'].iloc[i], self.restaurants['restaurant_name'].iloc[i])
            reviews_sub = reviews_list.get_reviews()
            self.reviews = pd.concat([self.reviews,reviews_sub], sort = False, ignore_index = True)
            self.reviews.to_csv(self.review_dir, index = False)
            self.restaurants.loc[i, 'reviews_last_updated'] = date.today()
            self.restaurants.to_csv(self.restaurant_dir, index = False)
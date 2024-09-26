import refresh_data
import os

if not os.path.exists('data'):
    os.makedirs('data')

data = refresh_data.refresh_data('data/restaurants.csv','data/reviews.csv','data/streetname.csv', initial = False)

data.parallel_refresh_restaurants(num_threads = 4)
data.parallel_refresh_details(num_threads = 4)
data.parallel_refresh_reviews(num_threads = 4)
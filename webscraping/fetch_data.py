import refresh_data

data = refresh_data.refresh_data('restaurants.csv','reviews.csv','streetname.csv', initial = True)

data.parallel_refresh_restaurants(4)
data.parallel_refresh_details(4)
data.parallel_refresh_reviews(4)
import pandas as pd

listing = pd.read_csv(r'listings_dec18.csv')    

listing['Date'] = pd.to_datetime(listing['last_scraped'])

listing = listing[['Date','scrape_id','name','neighbourhood']].rename(columns={
    'name':'Name',
    'neighbourhood':'Location',
    'scrape_id':'Scrape_ID'})

listing.to_csv(r'listings_dec18.csv')


calender = pd.read_csv(r'calendar_dec18.csv')    

calender.dropna(inplace=True)

calender.to_csv(r'calendar_dec18.csv')

reviews = pd.read_csv(r'reviews_dec18.csv')

reviews['date'] = pd.to_datetime(reviews['date'])
reviews.dropna(inplace=True)

reviews = reviews[['date','comments']]

reviews.to_csv(r'reviews_dec18.csv')

listings = pd.read_csv(r'listings_summary_dec18.csv')

listings.dropna(inplace=True)

listings = listings[['last_review','room_type']]

listings.reset_index(drop=True,inplace=True)

listings.to_csv(r'listings_summary_dec18.csv')
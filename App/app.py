# Importing all the required Libraries
from flask import Flask, request, render_template, Response, send_file
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import re
# import dask.dataframe as dd

# Initialize start_date and end_date
start_date = dt.datetime.strptime('10-11-2018', '%m-%d-%Y')
end_date = dt.datetime.strptime('12-22-2018', '%m-%d-%Y')

# Define a function to return Listing Data of a Selected Time Period
def listingFunc(suburb,count=100):
    # Reading the required Data
    listing = pd.read_csv('listings_dec18.csv')
    listing['Date'] = pd.to_datetime(listing['Date'])

    # listing = listing[['Date', 'Scrape_ID', 'Name', 'Location']]
    # Filtering the Data
    df = listing[listing['Location'] == suburb].head(count)

    df.to_csv('static/csvs/listingtemp.csv',index=False)


# Define a function to create a Chart for Price Properties
def chartPrices(start_date,end_date):
    # Reading the required Data
    calender = pd.read_csv('calendar_dec18.csv')
    
    # Processing Some Data
    calender['date'] = pd.to_datetime(calender['date'], dayfirst=True)
    calender['price'] = calender['price'].str.replace('$', '')
    
    # Filtering the Data
    inTime = calender[(calender['date'] >= start_date) & (calender['date'] <= end_date)]

    # Convert 'price' column to numeric data type
    inTime['price'] = pd.to_numeric(inTime['price'], errors='coerce')

    # Define custom value ranges and labels
    value_ranges = [100, 150, 200, 250, 300]

    # Create a histogram with custom value ranges and labels
    plt.figure(figsize=(8, 6))
    plt.hist(inTime['price'], bins=[100, 150, 200, 250, 300], edgecolor='black', alpha=0.7)
    plt.xlabel('Value Ranges')
    plt.ylabel('Frequency')
    plt.title('Price Distribution')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Set custom tick positions and labels for the x-axis
    plt.xticks(value_ranges)
    plt.savefig('static/images/plot.png')
    plt.clf()


# Define a function to count the number of people commenting containing given words
def numCommented(words):
    # Reading the required Data
    reviews = pd.read_csv('reviews_dec18.csv')

    # Changing DataType of the date
    reviews['date'] = pd.to_datetime(reviews['date'])

    # Filtering according to time and dropping rows with missing 'comments' values
    inTime = reviews[(reviews['date'] >= start_date) & (reviews['date'] <= end_date)].dropna(subset=['comments'])

    # Printing the Number of People commenting
    data = {}
    for word in words:
        data[word] = inTime[inTime['comments'].str.contains(word, na=False)]['comments'].count()

    return data

# Define a function to analyze the number of people living in shared/private/entire home
def areaAnalysis(suburb):
    # Using the data Needed
    listings = pd.read_csv('listings_summary_dec18.csv')

    # Converting into DateTime
    # listings['last_review'] = pd.to_datetime(listings['last_review'])

    # Filtering the data according to Time
    inTime = listings[listings['neighbourhood'] == suburb]

    # Filtering the data according to Place
    ploting = inTime['room_type'].value_counts()
    print(ploting)

    # Plotting the required Data
    plt.pie(explode=[0.1] * len(ploting), x=ploting, labels=ploting.index, autopct='%1.1f%%')
    plt.savefig('static/images/pie.png')


# Initialize the Flask app
app = Flask(__name__)

app.static_folder = 'static'

# Home Page for Our website
@app.route('/')
def date_form():
    return render_template('date_form.html')

# Saves Values in start_date and end_date
@app.route('/submit', methods=['POST'])
def process_dates():
    sDate = request.form['start_day']
    eDate = request.form['end_day']
    sMonth = request.form['start_month']
    eMonth = request.form['end_month']
    sYear = request.form['start_year']
    eYear = request.form['end_year']
    suburb = request.form['suburb']
    global start_date
    global end_date
    start_date = dt.datetime.strptime(f'{sDate}/{sMonth}/{sYear}', '%d/%m/%Y')
    end_date = dt.datetime.strptime(f'{eDate}/{eMonth}/{eYear}', '%d/%m/%Y')

    listingFunc(suburb)
    chartPrices(start_date,end_date)
    areaAnalysis(suburb)
    return Response(status=204)

# Listing Function in some Time Period
@app.route('/function1')
def function1():
    df = pd.read_csv('static/csvs/listingtemp.csv')

    # Check if the DataFrame is empty or contains data
    if df.empty:
        return render_template('noData.html')

    # Convert DataFrame to HTML table for rendering
    table_html = df.to_html(classes='table table-bordered table-striped', index=False)

    # Pass the HTML table to the template
    return render_template('function1.html', data=table_html)

# Chart Prices in Some Time Period
@app.route('/function2')
def function2():
    return send_file('static/images/plot.png', mimetype='image/png')


def highlight_keyword(comment, keyword):
    comment = re.sub(rf'\b({re.escape(keyword)})\b', r'<b><mark>\1</mark></b>', comment, flags=re.IGNORECASE)
    return comment

# Cleanliness Reviews in Some Time Period
@app.route('/function3', methods=['GET', 'POST'])
def index():
    df = pd.read_csv('reviews_dec18.csv')
    df['date'] = pd.to_datetime(df['date'])  # Convert 'date' column to datetime

    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    if request.method == 'POST':
        # Get the user-inputted keyword from the form
        keyword = request.form.get('keyword').strip()

        # Filter reviews containing the keyword
        filtered_df = df[df['comments'].str.contains(keyword, case=False, na=False)]
        commnum = len(filtered_df) # Use len() to get the number of rows
        
        # Apply the highlighting function to the filtered reviews
        filtered_df['highlighted_comments'] = filtered_df['comments'].apply(highlight_keyword, keyword=keyword)

        return render_template('function3.html', keyword=keyword, filtered_df=filtered_df, commnum=str(commnum))
    
    return render_template('function3.html')

# Comments with words mentioned in it
@app.route('/function4')
def function4():
    data = numCommented(['clean', 'neat', 'tidy', 'elegant', 'spotless'])
    return render_template('function4.html', word_counts=data)

# Prints Pie chart of location using Place and Time Period
@app.route('/function5')
def function5():
    return send_file('static/images/pie.png', mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
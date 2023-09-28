#-------------------------Importing all the required Libraries--------------------------
from flask import Flask, request, render_template, Response, send_file
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import re

start_date = dt.datetime.strptime('10-11-2018','%m-%d-%Y')
end_date = dt.datetime.strptime('12-22-2018','%m-%d-%Y')

#---------------------------------FUNCTIONS DEFINED HERE----------------------------------
def listingFunc(count=100) -> pd.DataFrame:
    """
    To Return Listing Data of a Selected Time Period
    """
    #Reading the required Data
    listing = pd.read_csv(r'listings_dec18.csv')    
    listing['Date'] = pd.to_datetime(listing['Date'])

    listing = listing[['Date','Scrape_ID','Name','Location']]
    #Flitering the Data
    return listing[(listing['Date'] >= start_date) & (listing['Date'] <= end_date)].head(count)


def chartPrices() -> None: 
    """
    To create Chart for Price Properties.
    """
    #Reading the required Data
    calender = pd.read_csv(r'calendar_dec18.csv',dayfirst=True)    

    #Processing Some Data
    # calender.dropna(inplace=True)
    #To Add new Date Format column
    calender['date'] = pd.to_datetime(calender['date'])    

    #Flitering the Data
    inTime = calender[(calender['date'] >= start_date)&(calender['date'] <= end_date)] 

    #Plotting Required Figure
    plt.figure(figsize=(10,10))
    plt.gca().set_xticklabels([])
    sns.histplot(data=inTime,x='price',kde=True,bins=10)
    plt.savefig(r"static/images/plot.png")
    plt.clf()

def numCommented(words:list) -> dict:
    """
    Number of people commentes containg the given words.
    """
    #Reading the required Data
    reviews = pd.read_csv(r'reviews_dec18.csv')

    #Changing DataType of the date.
    reviews['date'] = pd.to_datetime(reviews['date'])
    # reviews.dropna(inplace=True)

    #Flitering accourding to time
    inTime = reviews[(reviews['date'] >= start_date) & (reviews['date'] <= end_date)]

    #Printing the Number of People commenting
    data = {}
    for word in words:
        data[word] = inTime[inTime['comments'].str.contains(word)]['comments'].count()
    
    return data
    

def areaAnalysis() -> pd.DataFrame:
    """
    Number of people Living in shared/private/entire home
    """
    #Using the data Needed
    listings = pd.read_csv(r'listings_summary_dec18.csv')

    #Modifying the Data
    # listings.drop('neighbourhood_group',axis=1,inplace=True)
    # listings.dropna(inplace=True)
    # listings.reset_index(drop=True,inplace=True)

    #Converting into DateTime
    listings['last_review'] = pd.to_datetime(listings['last_review'])

    #Flitering the data accourding to Time
    inTime = listings[(listings['last_review'] >= start_date) & (listings['last_review'] <= end_date)]

    #Flitering the data accourding to Place
    ploting = inTime['room_type'].value_counts()

    #Ploting the required Data
    plt.pie(explode=[0.1]*len(ploting),x=ploting,labels=ploting.index,autopct='%1.1f%%')
    plt.savefig(r'static/images/pie.png')


#--------------------------------------FLASK APP-----------------------------------------
app = Flask(__name__)

app.static_folder = 'static'

#Home Page for Our website
@app.route('/')
def date_form():
    return render_template('date_form.html')

#Saves Values in start_date and end_date
@app.route('/submit', methods=['POST'])
def process_dates():
    if request.method == 'POST':
        sDate = request.form['start_day']
        eDate = request.form['end_day']
        sMonth = request.form['start_month']
        eMonth = request.form['end_month']
        sYear = request.form['start_year']
        eYear = request.form['end_year']
        start_date = dt.datetime.strptime(f'{sMonth}/{sDate}/{sYear}', '%m/%d/%Y')
        end_date = dt.datetime.strptime(f'{eMonth}/{eDate}/{eYear}', '%m/%d/%Y')

    chartPrices()
    areaAnalysis()
    return Response(status=204)

#Listing Function in some Time Period
@app.route('/function1')
def function1():
    df = listingFunc(200).to_html()
    return render_template('function1.html', data=df)

#Chart Prices in Some Time Period
@app.route('/function2')
def function2():
    return send_file('static/images/plot.png', mimetype='image/png')


def highlight_keyword(comment, keyword):
    comment = re.sub(rf'\b({re.escape(keyword)})\b', r'<b><mark>\1</mark></b>', comment, flags=re.IGNORECASE)
    return comment

@app.route('/function3', methods=['GET', 'POST'])
def index():
    #Cleaniness Reviews in Some Time Period
    df = pd.read_csv('reviews_dec18.csv')
    df['date'] = pd.to_datetime(df['date'])  # Convert 'date' column to datetime

    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    if request.method == 'POST':
        # Get the user-inputted keyword from the form
        keyword = request.form.get('keyword').strip()

        # Filter reviews containing the keyword
        filtered_df = df[df['comments'].str.contains(keyword, case=False, na=False)]

        # Apply the highlighting function to the filtered reviews
        filtered_df['highlighted_comments'] = filtered_df['comments'].apply(highlight_keyword, keyword=keyword)

        return render_template('function3.html', keyword=keyword, filtered_df=filtered_df)

    return render_template('function3.html')


#Comments with words mentioned in it
@app.route('/function4')
def function4():
    data = numCommented(['clean','neat','tidy','elegant','spotless'])
    return render_template('function4.html', word_counts=data)

#Prints Pie chart of location using PLace and Time Period
@app.route('/function5')
def function5():
    return send_file('static/images/pie.png', mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)
import re
from datetime import datetime, timedelta
import pandas as pd
from bs4 import BeautifulSoup
import mechanize

from sheet_utils import *

BASE_URL = 'https://webb-site.com'
br = mechanize.Browser()

def get_currents_url(base_url, navigate_current=False):
    if navigate_current:
        # Navigate to get current_url from f1
        br.open(base_url+'/dbpub')
        br.select_form(name='f1')
        br.form.set_value(stock_code, 'code')
        br.submit()

    else:
        # Open the current url directly
        current_url = '{0}/dbpub/orgdata.asp?code={1}&Submit=current'.format(base_url, stock_code)
        br.open(current_url)

    # Follow the CCASS link
    br.follow_link(text='CCASS')

    # Follow the Changes link
    br.follow_link(text='Changes')

    # Select the filter form, set the dates range
    br.select_form(predicate=lambda f: f.attrs.get('action') == 'chldchg.asp')
    br.form.set_value(d1, id='d1')
    br.submit()
        
    return br.geturl()


def generate_change_links(base_url, stock_code, days=1):
    # Calculate the start date
    d1 = datetime.now().date() - timedelta(days=days)
    d1 = d1.strftime('%Y-%m-%d')
    
    # Navigate to get issue for changes
    #change_url = get_currents_url(base_url)

    # Go directly to the changes using stock code
    change_url = '{0}/ccass/chldchg.asp?sort=chngdn&sc={1}&d1={2}'.format(base_url, stock_code, d1)
    br.open(change_url)
        
    # Get all the change history for stakeholders
    return br.links(url_regex=r'chistory')


def capture_changes_data(link):
    print('Processing:', link.url)
    # Open the link and grab the page
    res = br.follow_link(link)
    page = BeautifulSoup(res.get_data(), 'lxml')

    # Pick the stock name and stakeholder name
    stock_name, stakeholder = [t.text for t in page.find_all('h2')]

    # Grab the last table on the page
    table = page.find_all('table')[-1]

    # Transform the table into pandas dataframe
    df = pd.read_html(str(table), header=0)[0]
        
    return stock_name, stakeholder, df


def prepare_values(df):
    df = df.fillna('').astype(str)
    return [df.columns.tolist()] + df.values.tolist()


def pull_data(url, stock_code, days):
    stock_name = ''
    counts = 0
    try:
        print('Extracting {0} days data for stock {1}'.format(days, stock_code) )
        # Generate the traget data links
        links_gen = generate_change_links(url, stock_code, days)
        
        for link in links_gen:
            # Grab the actual data
            stock_name, stakeholder, table = capture_changes_data(link)

            # Add the sheet
            sheet_name = '{0} | {1}'.format(stock_name, stakeholder)
            add_sheet(sheet_name)
            
            # Process the values and fill the sheet
            values = prepare_values(table)
            fill_sheet(sheet_name, values)
            print('{0} cells updated.'.format(len(values) ))
            counts +=1

        print('{0} data extracted successfully!'.format(stock_name))

    except Exception as e:
        print('Ops! Something is not right!')
        print(e)
        
    return stock_name, counts
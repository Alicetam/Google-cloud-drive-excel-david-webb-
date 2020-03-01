import os

from flask import Flask, request

from data_utils import *
from sheet_utils import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def run_scraping():
    if request.method == 'GET':
        data = request.args
    else:
        data = request.get_json()

    stock_code = data.get('stock_code') or '8495'
    days = int( data.get('days') or 1)
    
    print('Stock: {0}, Days: {1}'.format(stock_code, days) )

    # Start here
    stock_name, counts = pull_data(BASE_URL, stock_code, days)
    print('Pull data completed. Filling the sheets.')

    return '{0} tables pulled for {1}.'.format(counts, stock_name)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


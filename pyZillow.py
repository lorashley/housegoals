from bs4 import BeautifulSoup as BS
from flask import Flask, request, render_template
import json
import os
import propMongo
import re
import requests
import usaddress as usa
from walkscore.api import WalkScore

# Init Flask
app = Flask(__name__)


def get_search_results(url):
    return requests.get(url)
    
def get_zpid(url):
    pattern = '\/(.*)_zpid'
    mo = re.search(pattern, url)
    if mo: 
        return mo.group(1)
    return
    
def get_address(url):
    # Example URL: https://www.zillow.com/homedetails/645-6TH-Ave-N-Saint-Petersburg-FL-33701/47111766_zpid/?fullpage=true
    pattern = 'homedetails\/(.*)\/\d'
    mo = re.search(pattern, url)
    if not mo:
        return
    
    addr = mo.group(1).replace('-',' ')
    us_addr = usa.parse(addr)
    
    address_types = ['AddressNumber', 'StreetName', 'StreetNamePostType', 'StreetNamePostDirectional']
    city_type = ['PlaceName']
    state_type = ['StateName']
    zip_type = ['ZipCode']
    
    address = ''
    city = ''
    state = ''
    zip = ''

    for item in us_addr:
        if item[1] in address_types:
            add = "{} ".format(item[0])
            address += add
        elif item[1] in city_type:
            add = "{} ".format(item[0])
            city += add
        elif item[1] in state_type:
            state += item[0]
        elif item[1] in zip_type:
            zip += item[0]           

    return address.strip(), city.strip(), state, zip

def format_query_search(zws_id, address, city, state, zip):
    # url = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm?zws-id={}&address=2114+Bigelow+Ave&citystatezip=Seattle%2C+WA'.format(ws_id)
    address = address.replace(' ','+')
    query = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm?zws-id={}&address={}&citystatezip={}%2C+{}'.format(zws_id, address, city, state)
    return query
    
def get_property_details(url):
    # /47111766_zpid/
    get_prop_details = 'http://www.zillow.com/webservice/GetUpdatedPropertyDetails.htm?zws-id={}&zpid={}'.format(zws_id, get_zpid(url))
    resp = requests.get(get_prop_details)
    return resp.text

def parse_results(data):
    soup = BS(data, "lxml")
    
    #list of properties to collect
    find_list = ['address', 'amount', 'city', 'state', 'zipcode', 'homedetails', 'bedrooms', 'bathrooms', 'lotSizeSqFt', 'finishedSqFt', 'zpid', 'useCode']
    
    property = {}
    for item in find_list:
        try:
            info = soup.find(item.lower()).text
        except AttributeError:
            print("Unable to retrieve data for: {}".format(item))
            info = 'n/a1'
        property[item] = info
    return property
    
def getOtherAPIs(property):
    walk_token = os.environ.get('WALKSCORE_TOKEN')
    walkscore = WalkScore(walk_token)
    address = property['full_addr']
    print(walkscore.makeRequest(address))
    
    school_token = os.environ.get('SCHOOL_TOKEN')
    return

def start():
    url = input("Please enter Zillow URL: ")

def main(url, zws_id, ss_at, sheet_id): 
    if not url:
        url = 'https://www.zillow.com/homedetails/645-6TH-Ave-N-Saint-Petersburg-FL-33701/47111766_zpid/?fullpage=true'
        print("Entering sample URL:" + url)

    # Extract the address parts
    address, city, state, zip = get_address(url)
    
    # Format the zillow query
    query = format_query_search(zws_id, address, city, state, zip)
    
    # Get the data from the query and parse into a property dict
    data = get_search_results(query).text
    property = parse_results(data)
    property['full_addr'] = '{}. {}, {} {}'.format(address, city, state, zip)

    #Check if entry is in the mongo db, and add if not
    print(property)
    resp = propMongo.find_property(property, 'properties')
    if resp:
        print("Mongo entry already exists")
        return 200
    property = getOtherAPIs(property) # Call other APIs
    print("Adding entry to mongo")
    resp = propMongo.add_property(property, 'properties')
    return 200


        
#######################
# ROUTES
#######################

@app.route('/', methods=['GET'])
def landing():
    return render_template('landing.html')
    
@app.route('/', methods=['POST'])
def results():
    zws_id = os.environ.get('ZWS_ID') # Zillow ID
    ss_at = os.environ.get('SS_AT') # Smartsheet access token
    sheet_id = os.environ.get('SHEET_ID') # Smartsheet sheet ID
    
    url = request.form['url']
    status = main(url, zws_id, ss_at, sheet_id)
    if status == 200:
        return render_template('success.html') 
    elif status == 500:
        return render_template('failure.html') 
    return render_template('landing.html')    
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
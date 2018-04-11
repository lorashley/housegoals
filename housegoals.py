from bs4 import BeautifulSoup as BS
from flask import Flask, request, render_template
import json
import os
import propMongo
import pyZillow
import re
import requests
import usaddress as usa
import walk

# Init Flask
app = Flask(__name__)
    
def getOtherAPIs(property):
    address = property['full_addr'].replace(',','').replace('.','')
    lat = property['latitude']
    lon = property['longitude']
    score = walk.get_score(address, lat, lon)
    property['scores'] = score
    #school_token = os.environ.get('SCHOOL_TOKEN')
    return property

def main(url): 
    property = pyZillow.get_zillow_data(url)
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
    url = request.form['url']
    status = main(url)
    if status == 200:
        return render_template('success.html') 
    elif status == 500:
        return render_template('failure.html') 
    return render_template('landing.html')    

@app.route('/all', methods=['GET'])
def list():    
    col = 'properties'
    rows = propMongo.get_prop_list(col)
    return render_template('table.html', rows=rows)
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
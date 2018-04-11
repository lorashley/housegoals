import json
import requests
import urllib.parse

"""
http://api.walkscore.com/score?format=json&
address=1119%8th%20Avenue%20Seattle%20WA%2098101&lat=47.6085&
lon=-122.3295&transit=1&bike=1&wsapikey=<YOUR-WSAPIKEY>
"""

def get_score(address, lat, lon):
    api = os.environ.get('WALKSCORE_TOKEN')
    base_url = 'http://api.walkscore.com/score?format=json'
    address = '&address={}'.format(urllib.parse.quote(address))
    lat = '&lat={}'.format(lat)
    lon = '&lon={}'.format(lon)
    the_rest = '&transit=1&bike=1&wsapikey={}'.format(api)
    url = base_url + address + lat + lon + the_rest
    print("WALKSCORE URL:" + url)
    resp = requests.get(url)
    data = json.loads(resp.text)
    walkscore_data = {'walkscore': data['walkscore'],
                      'description': data['description'],
                      'transit': data['transit']['score'],
                      't_description': data['transit']['description'],
                      'bike': data['bike']['score'],
                      'b_description': data['bike']['description']}
    return walkscore_data

def main():
    address='1119 8th Avenue Seattle WA 98101'
    lat=47.6085
    lon=-122.3295
    print(get_score(address, lat, lon))

if __name__ == '__main__':
    main()
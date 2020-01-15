import json, urllib
import xmltodict
import logging
from urllib import request, parse
from .parser import search_result
from .proj_convertor import ProjConvertor
from .address_factory import AddressFactory

logger = logging.getLogger(__name__)

OGCIO_RECORD_COUNT = 200

def search_address_with_ogcio(address):
    ogcio_url = 'https://www.als.ogcio.gov.hk/lookup?q={}&n={}'.format(parse.quote(address), OGCIO_RECORD_COUNT)
    post_response = urllib.request.urlopen(url=ogcio_url)
    res = post_response.read()
    ogcio_data = json.dumps(xmltodict.parse(res), ensure_ascii=False)
    ogcio_data = json.loads(ogcio_data)
    searched_result = search_result(address, ogcio_data)
    return searched_result
    

def search_address_from_land(address):
    land_url = 'https://geodata.gov.hk/gs/api/v1.0.0/locationSearch?q={}'.format(parse.quote(address))
    post_response = urllib.request.urlopen(url=land_url)
    res = post_response.read()
    land_data = json.loads(res)
    land_records = []
    for data in land_data:
        # TODO: check if def is needed 
        proj = ProjConvertor("EPSG:2326", "EPSG:4326", data['x'], data['y'])
        lat, lng = proj.transform_projection()
        
        data['lat'] = float("{0:.4f}".format(lat))
        data['lng'] = float("{0:.4f}".format(lng))

        address_factory = AddressFactory("land", data)
        land_records.append(address_factory.create_address())

def query_address(address):
    print("queryAddress")
    ogcio_records = search_address_with_ogcio(address)
    land_records = search_address_from_land(address)

def batch_query_addresses(address):
    print("batchQueryAddresses")
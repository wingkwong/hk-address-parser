import json, urllib
import xmltodict
import logging
import concurrent.futures
from urllib import request, parse
from .parser import search_result
from .proj_convertor import ProjConvertor
from .address_factory import AddressFactory

logger = logging.getLogger(__name__)

OGCIO_RECORD_COUNT = 200
NEAR_THRESHOLD = 0.05  # 50 metres


def search_address_with_ogcio(address):
    ogcio_url = "https://www.als.ogcio.gov.hk/lookup?q={}&n={}".format(
        parse.quote(address), OGCIO_RECORD_COUNT
    )
    post_response = urllib.request.urlopen(url=ogcio_url)
    res = post_response.read()
    ogcio_data = json.dumps(xmltodict.parse(res), ensure_ascii=False)
    ogcio_data = json.loads(ogcio_data)
    searched_result = search_result(address, ogcio_data)
    ocgio_records = []

    for data in searched_result:
        address_factory = AddressFactory("ogcio", data)
        ocgio_records.append(address_factory.create_address())
    return ocgio_records


def search_address_from_land(address):
    land_url = "https://geodata.gov.hk/gs/api/v1.0.0/locationSearch?q={}".format(
        parse.quote(address)
    )
    post_response = urllib.request.urlopen(url=land_url)
    res = post_response.read()
    land_data = json.loads(res)
    land_records = []

    for data in land_data:
        # TODO: check if def is needed
        proj = ProjConvertor("EPSG:2326", "EPSG:4326", data["x"], data["y"])
        lat, lng = proj.transform_projection()

        data["lat"] = float("{0:.4f}".format(lat))
        data["lng"] = float("{0:.4f}".format(lng))

        address_factory = AddressFactory("land", data)
        land_records.append(address_factory.create_address())
    return land_records


def query_address(address):
    # Fetch records from OGCIO & Land Department
    ogcio_records = search_address_with_ogcio(address)
    land_records = search_address_from_land(address)

    sorted_results = []

    # if records from Land Department have any exception
    if len(land_records) == 0:
        return ogcio_records

    # 1. Best Case: Top OGCIO result appears in land result(s)
    # We compared with the first in land result but some cases that sometime the most accurate result does not appear at top
    # so we should search among the whole list

    for land_record in land_records:
        if ogcio_records[0].distance_to(land_record) < NEAR_THRESHOLD:
            # Best Case: Land result and ogcio return the same address
            return ogcio_records

    # 2. best result from OGCIO does not appears in the land results
    # so we pick the first land result as our destination and search all the OGCIO results and see if some result is within the NEAR_DISTANCE
    # and sort them with distance to the first land result

    for ogcio_record in ogcio_records:
        distance = ogcio_record.distance_to(land_records[0])

        if distance < NEAR_THRESHOLD:
            ogcio_record["distance"] = distance
            sorted_results.append(ogcio_record)

    if len(sorted_results) > 0:
        return sorted_results.sort(key=lambda record: record.distance)

    # 3. Not found in OGCIO but in land result.
    # We try to search again from ogcio using the land result
    assumed_land_result = land_records[0]
    full_address_to_search = land_records[0].full_address("chi")
    if full_address_to_search != "":
        ogcio_records = search_address_with_ogcio(full_address_to_search)
        if ogcio_records[0].distance_to(assumed_land_result) < NEAR_THRESHOLD:
            # second round result is the nearest result
            return ogcio_records

    return land_records


def batch_query_addresses(addresses):
    records = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(query_address, address) for address in addresses]
        for future in concurrent.futures.as_completed(futures):
            records.append(future.result())
    return records

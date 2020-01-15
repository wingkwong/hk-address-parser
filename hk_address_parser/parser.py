import re, json
import hk_address_parser.constant as constant
from functools import reduce
from operator import attrgetter


def search_result(address, response_from_ogcio):
    normalized_address = remove_floor(address).upper()
    normalized_ogcio_result = normalize_response(response_from_ogcio)
    return parse_address(normalized_address, normalized_ogcio_result)


def remove_floor(address):
    return re.sub(r"/([0-9A-z\-\s]+[樓層]|[0-9A-z號\-\s]+[舖鋪]|地[下庫]|平台).*/g", "", address)


def normalize_response(response_from_ogcio):
    return list(
        map(
            (
                lambda record:  
                (
                    {
                        'chi': eliminate_lang_keys(record['Address']['PremisesAddress']['ChiPremisesAddress']),
                        'eng': eliminate_lang_keys(record['Address']['PremisesAddress']['EngPremisesAddress']),
                        'geo': record['Address']['PremisesAddress']['GeospatialInformation']
                    }
                )
            ), 
            response_from_ogcio['AddressLookupResult']['SuggestedAddress']
        )
    )


def parse_address(address, normalized_ocgio_result):
    for record in normalized_ocgio_result:
        matches = find_match_from_ogcio_record(address, record)
        record['score'] = calculate_score_from_matches(matches)
        record['matches'] = matches
        record = transform_district(record)
    normalized_ocgio_result = sorted(normalized_ocgio_result, key=lambda record: record['score'])
    return normalized_ocgio_result[0:200]


def transform_district(ogcio_record):
    if ogcio_record['eng']['District']:
        ogcio_record['eng']['District']['DcDistrict'] = dc_district_mapping( ogcio_record['eng']['District']['DcDistrict'], False)

    if ogcio_record['chi']['District']:
        ogcio_record['chi']['District']['DcDistrict'] = dc_district_mapping( ogcio_record['chi']['District']['DcDistrict'], False)

    if ogcio_record['eng']['Region']:
         ogcio_record['eng']['Region'] = region_mapping(ogcio_record['eng']['Region'])
    
    return ogcio_record


def dc_district_mapping(val, is_chinese):
    dc_district = constant.DC_DISTRICT
    for district in dc_district:
        if district == val:
            if is_chinese:
                return dc_district[district]['chi']
            else:
                return dc_district[district]['eng']
    if is_chinese:
        return dc_district['invalid']['chi']
    else:
        return dc_district['invalid']['eng']
    

def region_mapping(val):
    region = constant.REGION
    for reg in region:
        if reg == val:
            return region[reg]['eng']


def eliminate_lang_keys(record):
    result = {}
    for attr, value in record.items():
        refined_key = re.sub("^(Chi|Eng)", '', attr)
        if type(value) == dict:
            result[refined_key] = eliminate_lang_keys(value)
        else:
            result[refined_key] = value
    return result


def find_match_from_ogcio_record(address, ogcio_record):
    matches = []
    for key in constant.ELEMENT_PRIORITY:
        if key in ogcio_record['chi'] and is_chinese(address):
            occurance = search_occurance(address, key, ogcio_record['chi'][key])

            if occurance is None:
                continue
            
            matches.append(occurance)

        if key in ogcio_record['eng'] and not is_chinese(address):
            occurance = search_occurance(address, key, ogcio_record['eng'][key])
            if occurance is None:
                continue
            matches.append(occurance)
    return find_maximum_non_overlapping_matches(address, matches)


def is_chinese(s):
    return re.search(r"/[^\u0000-\u00ff]/", s)


def search_occurance(address, ogcio_record_elementKey, ogcio_record_element):
    switcher = {
        constant.OGCIO_KEY_STREET:           lambda: search_occurance_for_street(address, ogcio_record_element),
        constant.OGCIO_KEY_VILLAGE:          lambda: search_occurance_for_village(address, ogcio_record_element),
        constant.OGCIO_KEY_BLOCK:            lambda: search_occurance_for_block(address, ogcio_record_element),
        constant.OGCIO_KEY_PHASE:            lambda: search_occurance_for_phase(address, ogcio_record_element),
        constant.OGCIO_KEY_ESTATE:           lambda: search_occurance_for_estate(address, ogcio_record_element),
        constant.OGCIO_KEY_REGION:           lambda: search_occurance_for_region(address, ogcio_record_element),
        constant.OGCIO_KEY_BUILDING_NAME:    lambda: search_occurance_for_building_name(address, ogcio_record_element)
    }
    
    return switcher.get(
        ogcio_record_elementKey,
        None
    )()

def search_occurance_for_street(address, ogcio_record_element):
    street_name = ogcio_record_element.get('StreetName', None)
    building_no_from = ogcio_record_element.get('BuildingNoFrom', None)
    building_no_to = ogcio_record_element.get('BuildingNoTo', None)
    address_to_be_searched = split_value_for_space_if_chinese(street_name)
    return search_similarity_for_street_or_village(constant.OGCIO_KEY_STREET, address, address_to_be_searched, building_no_from, building_no_to)


def search_occurance_for_village(address, ogcio_record_element):
    village_name = ogcio_record_element.get('VillageName', None)
    building_no_from = ogcio_record_element.get('BuildingNoFrom', None)
    building_no_to = ogcio_record_element.get('BuildingNoTo', None)
    address_to_be_searched = split_value_for_space_if_chinese(village_name)
    return search_similarity_for_street_or_village(constant.OGCIO_KEY_VILLAGE, address, address_to_be_searched, building_no_from, building_no_to)


def search_occurance_for_block(address, ogcio_record_element):
    block_descriptor = ogcio_record_element['BlockDescriptor']
    block_no = ogcio_record_element['BlockNo']
    if address in block_no + block_descriptor:
        match = Match(
            constant.CONFIDENT_ALL_MATCH,
            constant.OGCIO_KEY_BLOCK
            [
                block_no,
                block_descriptor
            ]
        )

        if block_no:
            if not try_to_match_any_number(
                address,
                int(block_no)
            ):
                match.confident = constant.CONFIDENT_MULTIPLIER_NAME_ONLY
            return match

    return None 


def search_occurance_for_phase(address, ogcio_record_element):
    phase_no = ogcio_record_element['PhaseNo']
    phase_name = ogcio_record_element['PhaseName']
    if address in phase_name + phase_no:
        match = Match(
            constant.CONFIDENT_ALL_MATCH,
            constant.OGCIO_KEY_BLOCK,
            [
                phase_no,
                phase_name
            ]
        )
        
        if phase_no:
            if not try_to_match_any_number(
                address,
                int(phase_no)
            ):
                match.confident = constant.CONFIDENT_MULTIPLIER_NAME_ONLY
            return match

    return None 


def search_occurance_for_estate(address, ogcio_record_element):
    estate_name = ogcio_record_element['EstateName']
    if address in estate_name:
        return Match(
            constant.CONFIDENT_ALL_MATCH, 
            constant.OGCIO_KEY_ESTATE,
            [
                estate_name
            ]
        )
    return None


def search_occurance_for_region(address, region):
    if address in region:
        return Match(
            constant.CONFIDENT_ALL_MATCH, 
            constant.OGCIO_KEY_ESTATE,
            [
                region
            ]
        )
    return None


def search_occurance_for_building_name(address, building_name):
    if address in building_name:
        return Match(
            constant.CONFIDENT_ALL_MATCH, 
            constant.OGCIO_KEY_ESTATE,
            [
                building_name
            ]
        )
    else:
        match_percentage, match_word = find_partial_match(address, building_name)
        if match_percentage > 0:
            match = Match(
                constant.CONFIDENT_ALL_MATCH, 
                constant.OGCIO_KEY_ESTATE,
                [
                    match_word
                ]
            )
            match.confident = modify_confident_by_partial_match_percentage(
                match.confident, 
                match_percentage
            )
            return match
        return None


def split_value_for_space_if_chinese(value):
    if is_chinese(value) and re.search(r"/\s/", value):
        tokens = re.split(r"/\s/")
        return tokens[-1]
    return value


def search_similarity_for_street_or_village(type, address, address_to_search, building_no_from, building_no_to):
    sim = Match(
        0,
        type,
        []
    )

    if address in address_to_search:
        sim.confident = constant.CONFIDENT_ALL_MATCH
        sim.matched_words.append(address_to_search)
    else:
        match_percentage, match_word = find_partial_match(address, address_to_search)
        if match_percentage > 0:
            sim.confident = modify_confident_by_partial_match_percentage(constant.CONFIDENT_ALL_MATCH, match_percentage)
            sim.matched_words.append(match_word)

    if building_no_from:
        no_from = int(re.sub("\D", "", building_no_from))
        if building_no_to:
            no_to = int(re.sub("\D", "", building_no_to))
        else: 
            no_to = no_from 

        isOdd = int(no_from) % 2 == 1
    
        if no_from == no_to:
            if not try_to_match_any_number(address, no_from):
                if tryToMatchRangeOfNumber(address, no_from, no_to, not isOdd):
                    sim.confident *= constant.CONFIDENT_MULTIPLIER_OPPOSITE_STREET
                else:
                    sim.confident *= constant.CONFIDENT_MULTIPLIER_NAME_ONLY
            else:
                sim.matched_words.append(no_from + '')
                sim.confident *= constant.CONFIDENT_MULTIPLIER_FULL_STREET_MATCH
        else:
            if not tryToMatchRangeOfNumber(address, no_from, no_to, isOdd):
                if tryToMatchRangeOfNumber(address, no_from, no_to, not isOdd):
                     sim.confident *= constant.CONFIDENT_MULTIPLIER_OPPOSITE_STREET
                else:
                    sim.confident *= constant.CONFIDENT_MULTIPLIER_NAME_ONLY
            else:
                # TODO: cannot mark the street/village number that we have came across
                sim.confident *= constant.CONFIDENT_MULTIPLIER_FULL_STREET_MATCH
    else:
        sim.confident *= constant.CONFIDENT_MULTIPLIER_NAME_ONLY
    return sim

def try_to_match_any_number(address, number):
    matches = re.match(r"/\d+/g", address)
    if matches is None:
        return False
    
    for match in matches:
        num = int(match)
        if num == number:
            return True 

    return False


def tryToMatchRangeOfNumber(address, no_from, no_to, isOdd):
    matches = re.match(r"/\d+/g", address)
    if matches is None:
        return False
    
    for match in matches:
        num = int(match)
        if num >= no_from and num <= no_to and ( (num % 2 == 1) == isOdd ):
            return True

    return False


def find_partial_match(string, string_to_search):
    match = {
        'match_percentage': 0,
        'matched_word': None
    }
    if string_to_search in string:
        match['match_percentage'] = 0.9
        match['matched_word'] = string
    else:   
        break_loop = False
        for i in range(0, len(string_to_search)):
            for j in range(len(string_to_search), i):
               substring = string_to_search[i, j]
               if string in substring:
                    match['match_percentage'] = len(substring) * 1.0 / len(substring)
                    match['matched_word'] = substring
                    break_loop = True
                    break
            if break_loop: 
                break
    return match['match_percentage'], match['matched_word']


def modify_confident_by_partial_match_percentage(confident, match_percentage):
    return confident * match_percentage * match_percentage * constant.CONFIDENT_MULTIPLIER_PARTIAL_MATCH


def find_maximum_non_overlapping_matches(address, matches):
    if len(matches) == 1:
        if matches[0].matched_words is not None and match_all_matched_words(address, matches[0].matched_words):
            return matches
        return []

    longest_match_score = 0
    longest_match = []
    
    for match in matches:
        if match_all_matched_words(address, match.matched_words):
            sub_address = address
            for word in match.matched_words:
                sub_address = sub_address.replace(word, '')

            local_longest_match = find_maximum_non_overlapping_matches(sub_address, [ _match for _match in matches if _match.matched_key != match.matched_key ])
            local_longest_match.append(match)
            score = calculate_score_from_matches(local_longest_match)
            if score > longest_match_score:
                longest_match_score = score
                longest_match = local_longest_match
    return longest_match


def match_all_matched_words(address, matched_words):
    address_includes_word = map(lambda matched_words, address: matched_words in address, matched_words, address )
    
    return reduce(
        lambda p, c:
            ( p and c ),
            [address_includes_word]
    )


def calculate_score_from_matches(matches):
    score = 0
    if matches is None:
        return score

    for match in matches:
        score += constant.SCORE_SCHEME[match.matched_key] * match.confident
    return score


class Match:
    def __init__(self, confident, matched_key, matched_words):
        self.confident = confident
        self.matched_key = matched_key
        self.matched_words = matched_words

    def __repr__(self):
        return "Match({}, {}, {})".format(self.confident, self.matched_key, self.matched_words)
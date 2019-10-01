import re, json
from .constant import constant
from functools import reduce
from operator import attrgetter


def searchResult(address, responseFromOGCIO):
    normalizedAddress = removeFloor(address).upper()
    normalizedOGCIOResult = normalizeResponse(responseFromOGCIO)
    return parseAddress(normalizedAddress, normalizedOGCIOResult)


def removeFloor(address):
    return re.sub(r"/([0-9A-z\-\s]+[樓層]|[0-9A-z號\-\s]+[舖鋪]|地[下庫]|平台).*/g", "", address)


def normalizeResponse(responseFromOGCIO):
    return list(
        map(
            (
                lambda record:  
                (
                    {
                        'chi': eliminateLangKeys(record['Address']['PremisesAddress']['ChiPremisesAddress']),
                        'eng': eliminateLangKeys(record['Address']['PremisesAddress']['EngPremisesAddress']),
                        'geo': record['Address']['PremisesAddress']['GeospatialInformation']
                    }
                )
            ), 
            responseFromOGCIO['AddressLookupResult']['SuggestedAddress']
        )
    )


def parseAddress(address, normalized_ocgio_result):
    for record in normalized_ocgio_result:
        matches = findMatchFromOGCIORecord(address, record)
        record['score'] = calculateScoreFromMatches(matches)
        record['matches'] = matches
        record = transformDistrict(record)

    normalized_ocgio_result = sorted(normalized_ocgio_result, key=attrgetter('score'))
    return normalized_ocgio_result[0:200]


def transformDistrict(ogcio_record):
    if ogcio_record['eng']['District']:
        ogcio_record['eng']['District']['DcDistrict'] = dcDistrictMapping( ogcio_record['eng']['District']['DcDistrict'], False)

    if ogcio_record['chi']['District']:
        ogcio_record['chi']['District']['DcDistrict'] = dcDistrictMapping( ogcio_record['chi']['District']['DcDistrict'], False)

    if ogcio_record['eng']['Region']:
         ogcio_record['eng']['Region'] = regionMapping(ogcio_record['eng']['Region'])
    
    return ogcio_record


def dcDistrictMapping(val, is_chinese):
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
    

def regionMapping(val):
    region = constant.REGION
    for reg in region:
        if reg == val:
            return region[reg]['eng']


def eliminateLangKeys(record):
    result = {}
    for attr, value in record.items():
        refinedKey = re.sub("^(Chi|Eng)", '', attr)
        if type(value) == dict:
            result[refinedKey] = eliminateLangKeys(value)
        else:
            result[refinedKey] = value
    return result


def findMatchFromOGCIORecord(address, ogcio_record):
    matches = []
    for key in constant.ELEMENT_PRIORITY:
        if ogcio_record['chi'][key] is not None and not isChinese(address):
            occurance = searchOccurance(address, key, ogcio_record['chi'][key])

            if occurance is None:
                continue
            
            matches.append(occurance)

        if ogcio_record['eng'][key] is not None and not isChinese(address):
            occurance = searchOccurance(address, key, ogcio_record['eng'][key])
            if occurance is None:
                continue
            matches.append(occurance)
    return findMaximumNonOverlappingMatches(address, matches)


def calculateScoreFromMatches(matches):
    pass


def isChinese(s):
    return re.search(r"/[^\u0000-\u00ff]/", s)


def searchOccurance(address, ogcioRecordElementKey, ogcioRecordElement):
    switcher = {
        constant.OGCIO_KEY_STREET:           searchOccuranceForStreet(address, ogcioRecordElement),
        constant.OGCIO_KEY_VILLAGE:          searchOccuranceForVillage(address, ogcioRecordElement),
        constant.OGCIO_KEY_BLOCK:            searchOccuranceForBlock(address, ogcioRecordElement),
        constant.OGCIO_KEY_PHASE:            searchOccuranceForPhase(address, ogcioRecordElement),
        constant.OGCIO_KEY_ESTATE:           searchOccuranceForEstate(address, ogcioRecordElement),
        constant.OGCIO_KEY_REGION:           searchOccuranceForRegion(address, ogcioRecordElement),
        constant.OGCIO_KEY_BUILDING_NAME:    searchOccuranceForBuildingName(address, ogcioRecordElement)
    }
    
    return switcher.get(
        ogcioRecordElementKey,
        None
    )

def searchOccuranceForStreet(address, ogcioRecordElement):
    street_name = ogcioRecordElement['StreetName']
    building_no_from = ogcioRecordElement['BuildingNoFrom']
    building_no_to = ogcioRecordElement['BuildingNoTo']
    address_to_be_searched = splitValueForSpaceIfChinese(street_name)
    return searchSimilarityForStreetOrVillage(constant.OGCIO_KEY_STREET, address, address_to_be_searched, building_no_from, building_no_to)


def searchOccuranceForVillage(address, ogcioRecordElement):
    village_name = ogcioRecordElement['VillageName']
    building_no_from = ogcioRecordElement['BuildingNoFrom']
    building_no_to = ogcioRecordElement['BuildingNoTo']
    address_to_be_searched = splitValueForSpaceIfChinese(village_name)
    return searchSimilarityForStreetOrVillage(constant.OGCIO_KEY_VILLAGE, address, address_to_be_searched, building_no_from, building_no_to)


def searchOccuranceForBlock(address, ogcioRecordElement):
    block_descriptor = ogcioRecordElement['BlockDescriptor']
    block_no = ogcioRecordElement['BlockNo']
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
            if not tryToMatchAnyNumber(
                address,
                int(block_no)
            ):
                match.confident = constant.CONFIDENT_MULTIPLIER_NAME_ONLY
            return match

    return None 


def searchOccuranceForPhase(address, ogcioRecordElement):
    phase_no = ogcioRecordElement['PhaseNo']
    phase_name = ogcioRecordElement['PhaseName']
    if address in phase_name + phase_no:
        match = Match(
            constant.CONFIDENT_ALL_MATCH,
            constant.OGCIO_KEY_BLOCK
            [
                phase_no,
                phase_name
            ]
        )
        
        if phase_no:
            if not tryToMatchAnyNumber(
                address,
                int(phase_no)
            ):
                match.confident = constant.CONFIDENT_MULTIPLIER_NAME_ONLY
            return match

    return None 


def searchOccuranceForEstate(address, ogcioRecordElement):
    estate_name = ogcioRecordElement['EstateName']
    if address in estate_name:
        return Match(
            constant.CONFIDENT_ALL_MATCH, 
            constant.OGCIO_KEY_ESTATE,
            [
                estate_name
            ]
        )
    return None


def searchOccuranceForRegion(address, region):
    if address in region:
        return Match(
            constant.CONFIDENT_ALL_MATCH, 
            constant.OGCIO_KEY_ESTATE,
            [
                region
            ]
        )
    return None


def searchOccuranceForBuildingName(address, building_name):
    if address in building_name:
        return Match(
            constant.CONFIDENT_ALL_MATCH, 
            constant.OGCIO_KEY_ESTATE,
            [
                building_name
            ]
        )
    else:
        match_percentage, match_word = findPartialMatch(address, building_name)
        if match_percentage > 0:
            match = Match(
                constant.CONFIDENT_ALL_MATCH, 
                constant.OGCIO_KEY_ESTATE,
                [
                    match_word
                ]
            )
            match.confident = modifyConfidentByPartialMatchPercentage(
                match.confident, 
                match_percentage
            )
            return match
        return None


def splitValueForSpaceIfChinese(value):
    if isChinese(value) and re.search(r"/\s/", value):
        tokens = re.split(r"/\s/")
        return tokens[-1]
    return value


def searchSimilarityForStreetOrVillage(type, address, address_to_search, building_no_from, building_no_to):
    sim = Match(
        0,
        type,
        []
    )

    if address in address_to_search:
        sim.confident = constant.CONFIDENT_ALL_MATCH
        sim.matchedWords.append(address_to_search)
    else:
        match_percentage, match_word = findPartialMatch(address, address_to_search)
        if match_percentage > 0:
            sim.confident = modifyConfidentByPartialMatchPercentage(constant.CONFIDENT_ALL_MATCH, match_percentage)
            sim.matchedWords.append(match_word)

    if building_no_from:
        no_from = int(building_no_from)
        if building_no_to:
            no_to = int(building_no_to)
        else: 
            no_to = no_from 

        isOdd = int(building_no_from) % 2 == 1
    
        if no_from == no_to:
            if not tryToMatchAnyNumber(address, no_from):
                if tryToMatchRangeOfNumber(address, no_from, no_to, not isOdd):
                    sim.confident *= constant.CONFIDENT_MULTIPLIER_OPPOSITE_STREET
                else:
                    sim.confident *= constant.CONFIDENT_MULTIPLIER_NAME_ONLY
            else:
                sim.matchedWords.append(no_from + '')
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

def tryToMatchAnyNumber(address, number):
    matches = re.match(r"/\d+/g")
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


def findPartialMatch(string, stringToSearch):
    match = {
        'match_percentage': 0,
        'matched_word': None
    }

    if stringToSearch.index(string):
        match.match_percentage = 0.9
        match.match_word = string
    else:   
        break_loop = False
        for i in range(0, stringToSearch.length):
            for j in range(stringToSearch.length, i):
               substring = stringToSearch[i, j]
               if string in substring:
                    match.match_percentage = len(substring) * 1.0 / len(substring)
                    match.match_word = substring
                    break_loop = True
                    break
            if break_loop: 
                break
    return match


def modifyConfidentByPartialMatchPercentage(confident, match_percentage):
    return confident * match_percentage * match_percentage * constant.CONFIDENT_MULTIPLIER_PARTIAL_MATCH

def filterMatchedKey(matches, target_matched_key):
    for match in matches:
        if match.matchedKey != target_matched_key:
            return True
        else:
            return False 


def findMaximumNonOverlappingMatches(address, matches):
    if len(matches) == 1:
        if matches[0]['matchedWord'] is not None and matchAllMatchedWords(address, matches[0].matchedWords):
            return matches
        return []

    longest_match_score = 0
    longest_match = []
    for match in matches:
        if matchAllMatchedWords(address, match.matchedWords):
            sub_address = address
            for word in match['matchedWords']:
                sub_address = sub_address.replace(word, '')
            local_longest_match = findMaximumNonOverlappingMatches(sub_address, matches.filter(filterMatchedKey, match.matchedKey))
            local_longest_match.append(match)
            score = calculateScoreFromMatches(local_longest_match)
            if score > longest_match_score:
                longest_match_score = score
                longest_match = local_longest_match


def matchAllMatchedWords(address, matched_words):
    address_includes_word = map(lambda matched_words, address: matched_words in address, matched_words, address )
    return reduce(
        lambda p, c:
            ( p and c ),
            address_includes_word
    )


def calculateScoreFromMatches(matches):
    score = 0
    for match in matches:
        score += constant.SCORE_SCHEME[match.matchedKey] * match.confident
    return score


class Match:
    def __init__(self, confident, matchedKey, matchedWords):
        self.confident = confident
        self.matchedKey = matchedKey
        self.matchedWords = matchedWords

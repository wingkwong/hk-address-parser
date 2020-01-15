CONFIDENT_ALL_MATCH = 1.0
CONFIDENT_MULTIPLIER_NAME_ONLY = 0.5
CONFIDENT_MULTIPLIER_PARTIAL_MATCH = 0.7
CONFIDENT_MULTIPLIER_OPPOSITE_STREET = 0.75
CONFIDENT_MULTIPLIER_FULL_STREET_MATCH = 1.5
CONFIDENT_REVERSE_MATCH = 0.9

OGCIO_KEY_BLOCK = "Block"
OGCIO_KEY_PHASE = "Phase"
OGCIO_KEY_ESTATE = "Estate"
OGCIO_KEY_VILLAGE = "Village"
OGCIO_KEY_STREET = "Street"
OGCIO_KEY_REGION = "Region"
OGCIO_KEY_BUILDING_NAME = "BuildingName"

SOURCE_OCGIO = "ogcio"
SOURCE_LAND = "land"

SCORE_SCHEME = {
    OGCIO_KEY_BUILDING_NAME: 50,
    OGCIO_KEY_VILLAGE: 40,
    OGCIO_KEY_ESTATE: 40,
    OGCIO_KEY_STREET: 40,
    OGCIO_KEY_REGION: 20,
    OGCIO_KEY_PHASE: 20,
    OGCIO_KEY_BLOCK: 20,
}

SCORE_PER_MATCHED_CHAR = 0.1

ELEMENT_PRIORITY = [
    OGCIO_KEY_BUILDING_NAME,
    OGCIO_KEY_BLOCK,
    OGCIO_KEY_PHASE,
    OGCIO_KEY_ESTATE,
    OGCIO_KEY_VILLAGE,
    OGCIO_KEY_STREET,
    OGCIO_KEY_REGION
]

REGION = {
  'HK': {
    'eng': "Hong Kong",
    'chi': "香港"
  },
  'KLN': {
    'eng': "Kowloon",
    'chi': "九龍"
  },
  'NT': {
    'eng': "New Territories",
    'chi': "新界"
  }
}

DC_DISTRICT = {
  'invalid': {
    'eng': "Invalid District Name",
    'chi': "無效地區"
  },
  'CW': {
    'eng': "Central and Western District",
    'chi': "中西區"
  },
  'EST': {
    'eng': "Eastern District",
    'chi': "東區"
  },
  'ILD': {
    'eng': "Islands District",
    'chi': "離島區"
  },
  'KLC': {
    'eng': "Kowloon City District",
    'chi': "九龍城區"
  },
  'KC': {
    'eng': "Kwai Tsing District",
    'chi': "葵青區"
  },
  'KT': {
    'eng': "Kwun Tong District",
    'chi': "觀塘區"
  },
  'NTH': {
    'eng': "North District",
    'chi': "北區"
  },
  'SK': {
    'eng': "Sai Kung District",
    'chi': "西貢區"
  },
  'ST': {
    'eng': "Sha Tin Distric",
    'chi': "沙田區"
  },
  'SSP': {
    'eng': "Sham Shui Po District",
    'chi': "深水埗區"
  },
  'STH': {
    'eng': "Southern District",
    'chi': "南區"
  },
  'TP': {
    'eng': "Tai Po District",
    'chi': "大埔區"
  },
  'TW': {
    'eng': "Tsuen Wan District",
    'chi': "荃灣區"
  },
  'TM': {
    'eng': "Tuen Mun District",
    'chi': "屯門區"
  },
  'WC': {
    'eng': "Wan Chai District",
    'chi': "灣仔區"
  },
  'WTS': {
    'eng': "Wong Tai Sin District",
    'chi': "黃大仙區"
  },
  'YTM': {
    'eng': "Yau Tsim Mong District",
    'chi': "油尖旺區"
  },
  'YL': {
    'eng': "Yuen Long District",
    'chi': "元朗區"
  }
}
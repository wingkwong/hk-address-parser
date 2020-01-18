"""
Some helper functions for showing OGCIO address result
Definations: https://www.als.ogcio.gov.hk/docs/Data_Dictionary_for_ALS_EN.pdf
"""
import logging

logger = logging.getLogger(__name__)

OGCIO_KEY_BLOCK = "Block"
OGCIO_KEY_PHASE = "Phase"
OGCIO_KEY_ESTATE = "Estate"
OGCIO_KEY_VILLAGE = "Village"
OGCIO_KEY_REGION = "Region"
OGCIO_KEY_STREET = "Street"
OGCIO_KEY_DISTRICT = "District"
OGCIO_KEY_LOT = "Lot"
OGCIO_KEY_STRUCTURED_LOT = "StructuredLot"
OGCIO_KEY_BUILDING_NAME = "BuildingName"

keys = {
    "eng": {
        # level 1 keys
        OGCIO_KEY_BLOCK: "Block",
        OGCIO_KEY_PHASE: "Phase",
        OGCIO_KEY_ESTATE: "Estate",
        OGCIO_KEY_VILLAGE: "Village",
        OGCIO_KEY_REGION: "Region",
        OGCIO_KEY_DISTRICT: "District",
        OGCIO_KEY_STREET: "Street",
        OGCIO_KEY_BUILDING_NAME: "Building Name",
        # level 2 keys
        OGCIO_KEY_DISTRICT: {"DcDistrict": "District"},
        OGCIO_KEY_STREET: {
            "StreetName": "Street Name",
            "BuildingNoFrom": "Street No. From",
            "BuildingNoTo": "Street No. To",
        },
        OGCIO_KEY_ESTATE: {"EstateName": "Estate Name"},
    },
    "chi": {
        # level 1 keys
        OGCIO_KEY_BLOCK: "座數",
        OGCIO_KEY_PHASE: "期數",
        OGCIO_KEY_ESTATE: "屋邨",
        OGCIO_KEY_VILLAGE: "鄉村",
        OGCIO_KEY_REGION: "區域",
        OGCIO_KEY_DISTRICT: "地區",
        OGCIO_KEY_STREET: "街道",
        OGCIO_KEY_BUILDING_NAME: "大廈名稱",
        # level 2 keys
        OGCIO_KEY_DISTRICT: {"DcDistrict": "區議會分區"},
        OGCIO_KEY_STREET: {
            "StreetName": "街道",
            "BuildingNoFrom": "街號",
            "BuildingNoTo": "街號",
        },
        OGCIO_KEY_ESTATE: {"EstateName": "屋邨"},
    },
}


def __safe_field_value(obj, key):
    if obj and obj["key"] is not None:
        return obj["key"]
    return None


def __eng_building_number_from_field(field):
    if field is None or (
        field["BuildingNoFrom"] is None and field["BuildingNoTo"] is None
    ):
        return ""

    build_no_from = field["BuildingNoFrom"]
    build_no_to = field["BuildingNoTo"]

    if build_no_from is not None and build_no_to is not None:
        return "{}-{}".format(build_no_from, build_no_to)
    else:
        if build_no_to is not None:
            return build_no_to
        else:
            return build_no_from


def __chi_building_number_from_field(field):
    if field is None or (
        field["BuildingNoFrom"] is None and field["BuildingNoTo"] is None
    ):
        return ""

    build_no_from = field["BuildingNoFrom"]
    build_no_to = field["BuildingNoTo"]

    if build_no_from is not None and build_no_to is not None:
        return "{}至{}號".format(build_no_from, build_no_to)
    else:
        if build_no_to is not None:
            return "{}號".format(build_no_to)
        else:
            return "{}號".format(build_no_from)


def __pretty_print_block(block, lang):
    if lang == "chi":
        return block["BlockNo"] + block["BlockDescriptor"]
    elif lang == "eng":
        return block["BlockDescriptor"] + " " + block["BlockNo"]
    else:
        logger.error("lang Not Supported. Accepted Types: chi or eng")
        return None


def __pretty_print_estate(estate, lang):
    estate_name = estate["EstateName"]
    phase = estate[OGCIO_KEY_PHASE]
    if lang == "chi":
        if phase is not None:
            estate_name = "{}{}{}".format(
                estate_name,
                __safe_field_value(estate[OGCIO_KEY_PHASE], "PhaseNo"),
                __safe_field_value(estate[OGCIO_KEY_PHASE], "PhaseName"),
            )
    elif lang == "eng":
        estate_name = "{}{}{}".format(
            estate_name,
            __safe_field_value(estate[OGCIO_KEY_PHASE], "PhaseName"),
            __safe_field_value(estate[OGCIO_KEY_PHASE], "PhaseNo"),
        )
    else:
        logger.error("lang Not Supported. Accepted Types: chi or eng")
    return estate_name


def __pretty_print_street(street, lang):
    if lang == "chi":
        return "{}{}".format(
            __safe_field_value(street, "StreetName"),
            __chi_building_number_from_field(street),
        )
    elif lang == "eng":
        return "{}{}".format(
            __eng_building_number_from_field(street),
            __safe_field_value(street, "StreetName"),
        )
    else:
        logger.error("lang Not Supported. Accepted Types: chi or eng")
        return None


def text_for_key(key, lang):
    if keys[lang] is not None:
        if keys[lang][key] is not None:
            return keys[lang][key]
    return key


def text_for_value(record, key, lang):
    if record[lang] is None:
        return None

    if type(record[lang[key]]) == "string":
        return record[lang][key]

    if key == OGCIO_KEY_ESTATE:
        return __pretty_print_estate(record[lang][key], lang)
    elif key == OGCIO_KEY_BLOCK:
        return __pretty_print_block(record[lang][key], lang)
    elif key == OGCIO_KEY_STREET:
        return __pretty_print_street(record[lang][key], lang)

    return ",".join(record.values())


def full_chinese_address_from_result(result):
    street = result["Street"]
    estate = result["Estate"]
    village = result["Village"]

    region = __safe_field_value(result, "Region")
    street_name = __safe_field_value(street, "StreetName")
    street_number = __chi_building_number_from_field(street)
    village_name = __safe_field_value(village, "VillageName")
    village_number = __chi_building_number_from_field(village)
    estate_name = __safe_field_value(estate, "EstateName")
    building_name = __safe_field_value(result, "BuildingName")

    return "{}{}{}{}{}{}{}".format(
        region,
        village_name,
        village_number,
        street_name,
        street_number,
        estate_name,
        building_name,
    ).strip()


def full_english_address_from_result(result):
    street = result["Street"]
    estate = result["Estate"]
    village = result["Village"]

    region = __safe_field_value(result, "Region")
    street_name = __safe_field_value(street, "StreetName")
    street_number = __eng_building_number_from_field(street)
    village_name = __safe_field_value(village, "VillageName")
    village_number = __eng_building_number_from_field(village)
    estate_name = __safe_field_value(estate, "EstateName")
    building_name = __safe_field_value(result, "BuildingName")
    # TODO: double check the format
    return "{}{}{}{}{}{}{}".format(
        region,
        village_name,
        village_number,
        street_name,
        street_number,
        estate_name,
        building_name,
    ).strip()

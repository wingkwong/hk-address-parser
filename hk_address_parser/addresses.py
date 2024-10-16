import geopy.distance
import logging
from hk_address_parser import ogcio_helper

logger = logging.getLogger(__name__)


class Address:
    lang_en = "eng"
    lang_zh = "chi"

    def __init__(self, record):
        self.record = record

    def __repr__(self):
        return "Address({})".format(self.record)

    @staticmethod
    def components(lang):
        return []

    @staticmethod
    def full_address(lang):
        return None

    @staticmethod
    def coordinate():
        return {"lat": 0, "lng": 0}

    @staticmethod
    def coordinates():
        return []

    @staticmethod
    def data_source():
        return None

    @staticmethod
    def confidence():
        return 0

    def distance_to(self, address):
        coord_1 = (self.coordinate()["lat"], self.coordinate()["lng"])
        coord_2 = (address.coordinate()["lat"], address.coordinate()["lng"])
        return geopy.distance.geodesic(coord_1, coord_2).km


class OGCIOAddress(Address):
    def __init__(self, record):
        self.flattened_components = None
        Address.__init__(self, record)

    def __repr__(self):
        return "OGCIOAddress({}, {}, {})".format(
            self.record, self.components("eng"), self.components("chi")
        )

    def components(self, lang):
        if self.flattened_components is None:
            self.flattened_components = self.flatten_components(lang)

        if lang == Address.lang_en:
            return self.flattened_components[Address.lang_en]
        else:
            return self.flattened_components[Address.lang_zh]

    def flatten_components(self, lang):
        flattened_components = {[Address.lang_en]: [], [Address.lang_zh]: []}

        langs = [Address.lang_zh, Address.lang_en]

        for lang in langs:
            for key in self.record[lang]:
                flattened_components[lang].append(
                    {
                        "key": key,
                        "translated_label": ogcio_helper.text_for_key(key, lang),
                        "translated_value": ogcio_helper.text_for_value(
                            self.record, key, lang
                        ),
                    }
                )

        return flattened_components

    def full_address(self, lang):
        if lang == Address.lang_en:
            return ogcio_helper.full_english_address_from_result(self.record["eng"])
        elif lang == Address.lang_zh:
            return ogcio_helper.full_english_address_from_result(self.record["chi"])
        else:
            logger.error("lang Not Supported. Accepted Types: chi or eng")
            return None

    def coordinate(self):
        g = {"lat": 0, "lng": 0}

        geo = self.record["geo"]

        if geo is not None and len(geo) > 0:
            g["lat"] = float(geo["Latitude"])
            g["lng"] = float(geo["Longitude"])

        return g

    def coordinates(self):
        geo = self.record["geo"]
        if geo is not None and len(geo) > 0:
            return list(
                map(
                    (
                        lambda g: {
                            "lat": float(g["Latitude"]),
                            "lng": float(g["Longitude"]),
                        }
                    ),
                    geo,
                )
            )
        return []

    @staticmethod
    def data_source(lang):
        if lang == Address.lang_en:
            return "Office of the Government Chief Information Officer"
        elif lang == Address.lang_zh:
            return "政府資訊科技總監辦公室"
        else:
            logger.error("lang Not Supported. Accepted Types: chi or eng")
            return ""

    @staticmethod
    def confidence():
        # TODO:
        return 0


class LandAddress(Address):
    def __init__(self, record):
        self.flattened_components = None
        Address.__init__(self, record)

    def __repr__(self):
        return "LandAddress({}, {}, {})".format(
            self.record, self.components("eng"), self.components("chi")
        )

    def components(self, lang):
        if lang == Address.lang_en:
            return [
                {
                    "key": "name",
                    "translated_label": "name",
                    "translated_value": self.record["nameEN"],
                }
            ]
        elif lang == Address.lang_zh:
            return [
                {
                    "key": "name",
                    "translated_label": "name",
                    "translated_value": self.record["nameZH"],
                }
            ]
        else:
            logger.error("lang Not Supported. Accepted Types: chi or eng")
            return []

    def full_address(self, lang):
        if lang == Address.lang_en:
            return self.record["addressEN"]
        elif lang == Address.lang_zh:
            return self.record["addressZH"]
        else:
            logger.error("lang Not Supported. Accepted Types: chi or eng")
            return None

    def coordinate(self):
        g = {"lat": 0, "lng": 0}

        lat = self.record["lat"]
        lng = self.record["lng"]

        if lat is not None and lng is not None:
            g["lat"] = float(lat)
            g["lng"] = float(lng)

        return g

    def coordinates(self):
        # TODO:
        return []

    @staticmethod
    def data_source(lang):
        if lang == Address.lang_en:
            return "Lands Department"
        elif lang == Address.lang_zh:
            return "地政總署"
        else:
            logger.error("lang Not Supported. Accepted Types: chi or eng")
            return ""

    @staticmethod
    def confidence():
        # TODO:
        return 0

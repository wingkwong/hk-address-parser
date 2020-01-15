

class Address:
    lang_en = "eng"
    lang_zh = "chi"

    def __init__(self, record):
        self.record = record

    @staticmethod
    def components(lang):
        return []

    @staticmethod
    def full_address(lang):
        return None

    @staticmethod
    def coordinate():
        return {
            "lat": 0,
            "lng": 0
        }

    @staticmethod
    def coordinates():
        return []

    @staticmethod
    def data_source():
        return None

    @staticmethod
    def confidence():
        return 0

    @staticmethod
    def distance_to(address):
        # TODO:
        pass


class OGCIOAddress(Address):
    def __init__(self, record):
        self.flattened_components = None
        Address.__init__(self, record)

    @staticmethod
    def components(self, lang):
        if self.flattened_components is None:
            self.flattened_components = self.flatten_components()

        if lang == Address.lang_en:
            return self.flattened_components[Address.lang_en]
        else:
            return self.flattened_components[Address.lang_zh]

    @staticmethod
    def flatten_components(self, lang):
        flattened_components = {
            [Address.lang_en]: [],
            [Address.lang_zh]: []
        }

        langs = [ Address.lang_zh, Address.lang_en ]

        for lang in langs:
            for key in self.record[lang]:
                # TODO: Add ogcio helper
                flattened_components[lang].append({
                    "key": key,
                    "translated_label": '',
                    "translated_value": ''
                })

        return flattened_components

    @staticmethod
    def full_address(lang):
        if lang == Address.lang_en:
            return '' #TODO: Add fullEnglishAddressFromResult
        else:
            return '' #TODO: Add fullChineseAddressFromResult

    @staticmethod
    def coordinate(self):
        g = {
            "lat": 0,
            "lng": 0
        }

        geo = self.record["geo"]
        
        if geo is not None and len(geo) > 0:
            g["lat"] = float(geo[0]["Latitude"])
            g["lng"] = float(geo[0]["Longitude"])
        
        return g

    @staticmethod
    def coordinates(self):
        geo = self.record["geo"]
        if geo is not None and len(geo) > 0:
            return list(
                map(
                    (lambda g: {
                        "lat": float(g["Latitude"]),
                        "lng": float(g["Longitude"])
                    }), geo
                )
            )
        return []

    @staticmethod
    def data_source(lang):
        if lang == Address.lang_en:
            return 'Office of the Government Chief Information Officer'
        else:
            return '政府資訊科技總監辦公室'

    @staticmethod
    def confidence():
        # TODO:
        pass


class LandAddress(Address):
    def __init__(self, record):
        self.flattened_components = None
        Address.__init__(self, record)

    #TODO:
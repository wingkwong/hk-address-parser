from .addresses import OGCIOAddress, LandAddress, Address
import hk_address_parser.constant as constant


class AddressFactory:
    def __init__(self, source, record):
        self.source = source
        self.record = record

    def create_address(self):
        source = self.source
        record = self.record

        if source == constant.SOURCE_OCGIO:
            return OGCIOAddress(record)
        elif source == constant.SOURCE_LAND:
            return LandAddress(record)
        else:
            return Address(record)

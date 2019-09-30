import logging
from  .resolver import queryAddress, batchQueryAddresses

logger = logging.getLogger(__name__)

class AddressParser:
    @classmethod
    def parse(cls, address):
        if isinstance(address, str):
            return cls.parseSingleAddress(address)
        elif isinstance(address, list):
            return cls.parseMultipleAddress(address)
        else:
            logger.error("Input Type Not Supported. Accepted Types: str or list")

    @staticmethod
    def parseSingleAddress(address):
        return queryAddress(address)

    @staticmethod
    def parseMultipleAddress(address):
        return batchQueryAddresses(address)
        
import logging
from  .resolver import query_address, batch_query_addresses

logger = logging.getLogger(__name__)

class AddressParser:
    @classmethod
    def parse(cls, address):
        if isinstance(address, str):
            return cls.parse_single_address(address)
        elif isinstance(address, list):
            return cls.parse_multiple_address(address)
        else:
            logger.error("Input Type Not Supported. Accepted Types: str or list")

    @staticmethod
    def parse_single_address(address):
        return query_address(address)

    @staticmethod
    def parse_multiple_address(address):
        return batch_query_addresses(address)
        
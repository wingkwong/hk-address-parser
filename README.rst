===============================
hk-address-parser - The Universal Python Library for HKAddressParser
===============================

hk-address-parser is a Python library for `Hong Kong Address Parser`_


.. _`Hong Kong Address Parser`: https://g0vhk-io.github.io/HKAddressParser

Getting Started
~~~~~~~~~~~~~~~
Assuming that you have Python and ``virtualenv`` installed:

.. code-block:: sh

    $ git clone https://github.com/wingkwong/hk-address-parser.git
    $ cd hk-address-parser
    $ virtualenv venv
    ...
    $ . venv/bin/activate
    $ pip install -r requirements.txt
    $ pip install -e .

Format the code before committing it using ``black``

.. code-block:: sh

    $ make black

Usage
~~~~~~~~~~~~~~~
Import the library

.. code-block:: python

    from hk_address_parser import AddressParser

Single Query

.. code-block:: python

    address = AddressParser.parse( "Eaton Hotel, 380 Nathan Road, Jordan")

Batch Query

.. code-block:: python

    addresses = AddressParser.parse(
        [
            "九龍觀塘海濱道 181號 9樓",
            "九龍長沙灣道 303號長沙灣政府合署 12樓",
            "九龍啟德協調道 3號工業貿易大樓 5樓",
            "香港中環統一碼頭道 38號海港政府大樓 7樓",
            "香港北角渣華道 333號北角政府合署 12樓1210-11室",
            "九龍旺角聯運街 30號旺角政府合署 5樓 503室",
            "九龍觀塘鯉魚門道 12號東九龍政府合署 7樓",
            "九龍深水埗南昌邨南昌社區中心高座 3樓",
            "九龍黃大仙龍翔道 138號龍翔辦公大樓 8樓 801室",
            "新界沙田上禾輋路 1號沙田政府合署 7樓 708-714室",
            "新界大埔墟鄉事會街 8號大埔綜合大樓 4樓",
            "新界荃灣大河道 60號雅麗珊社區中心 3樓",
            "新界屯門震寰路 16號大興政府合署 2樓 201室",
            "新界元朗橋樂坊 2號元朗政府合署暨大橋街市 12樓"
        ]

Methods
~~~~~~~~~~~~~~~
Return a flatten component of a given address.

.. code-block:: python

    address.components(lang)

Return a full address in a given language.

.. code-block:: python

    address.full_address(lang)

Return a coordinate of a given address. Used for single query. 

.. code-block:: python

    address.coordinate()

Return a list of coordinates of given addresses. Used for batch query.

.. code-block:: python

    address.coordinates()

Return the data source, either OCGIO or Land Department.

.. code-block:: python

    address.data_source(lang)

Return a confidence value of a given address.

.. code-block:: python

    address.confidence()
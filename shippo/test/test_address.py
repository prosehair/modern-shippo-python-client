import shippo
from shippo.test.helper import (
    DUMMY_ADDRESS,
    INVALID_ADDRESS,
    NOT_POSSIBLE_ADDRESS,
    ShippoTestCase,
)

from shippo.test.helper import shippo_vcr


class AddressTests(ShippoTestCase):
    request_client = shippo.http_client.RequestsClient

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/address")
    def test_invalid_create(self):
        address = shippo.Address.create(**INVALID_ADDRESS)
        self.assertEqual(address.is_complete, False)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/address")
    def test_create(self):
        address = shippo.Address.create(**DUMMY_ADDRESS)
        self.assertEqual(address.is_complete, True)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/address")
    def test_retrieve(self):
        address = shippo.Address.create(**DUMMY_ADDRESS)
        retrieve = shippo.Address.retrieve(address.object_id)
        self.assertCountEqual(address, retrieve)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/address")
    def test_invalid_retrieve(self):
        self.assertRaises(shippo.error.APIError, shippo.Address.retrieve, "EXAMPLE_OF_INVALID_ID")

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/address")
    def test_list_all(self):
        address_list = shippo.Address.all()
        self.assertTrue("results" in address_list)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/address")
    def test_list_page_size(self):
        pagesize = 1
        address_list = shippo.Address.all(size=pagesize)
        self.assertEqual(len(address_list.results), pagesize)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/address")
    def test_invalid_validate(self):
        address = shippo.Address.create(**NOT_POSSIBLE_ADDRESS)
        self.assertEqual(address.is_complete, True)
        address = shippo.Address.validate(address.object_id)
        self.assertEqual(address.is_complete, False)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/address")
    def test_validate(self):
        address = shippo.Address.create(**DUMMY_ADDRESS)
        self.assertEqual(address.is_complete, True)
        address = shippo.Address.validate(address.object_id)

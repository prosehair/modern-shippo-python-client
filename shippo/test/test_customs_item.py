import shippo
from shippo.test.helper import (
    DUMMY_CUSTOMS_ITEM,
    INVALID_CUSTOMS_ITEM,
    ShippoTestCase,
)

from shippo.test.helper import shippo_vcr


class CustomsItemTest(ShippoTestCase):
    request_client = shippo.http_client.RequestsClient

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/customs-item")
    def test_invalid_create(self):
        self.assertRaises(shippo.error.InvalidRequestError, shippo.CustomsItem.create, **INVALID_CUSTOMS_ITEM)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/customs-item")
    def test_create(self):
        customs_item = shippo.CustomsItem.create(**DUMMY_CUSTOMS_ITEM)
        self.assertEqual(customs_item.object_state, "VALID")

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/customs-item")
    def test_retrieve(self):
        customs_item = shippo.CustomsItem.create(**DUMMY_CUSTOMS_ITEM)
        retrieve = shippo.CustomsItem.retrieve(customs_item.object_id)
        self.assertCountEqual(customs_item, retrieve)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/customs-item")
    def test_invalid_retrieve(self):
        self.assertRaises(shippo.error.APIError, shippo.CustomsItem.retrieve, "EXAMPLE_OF_INVALID_ID")

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/customs-item")
    def test_list_all(self):
        customs_items_list = shippo.CustomsItem.all(size=10, page=1)
        self.assertTrue("results" in customs_items_list)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/customs-item")
    def test_list_page_size(self):
        pagesize = 1
        customs_items_list = shippo.CustomsItem.all(size=pagesize)
        self.assertEqual(len(customs_items_list.results), pagesize)

from datetime import datetime

import shippo
from tests.helper import DUMMY_ORDER, ShippoTestCase, shippo_vcr


class OrderTests(ShippoTestCase):
    request_client = shippo.http_client.RequestsClient

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/order")
    def test_invalid_create(self):
        self.assertRaises(shippo.error.InvalidRequestError, shippo.Order.create)

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/order")
    def test_create(self):
        ORDER = DUMMY_ORDER
        ORDER["placed_at"] = datetime.now().isoformat() + "Z"
        order = shippo.Order.create(**ORDER)
        self.assertEqual(order.order_status, "PAID")

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/order")
    def test_retrieve(self):
        ORDER = DUMMY_ORDER
        ORDER["placed_at"] = datetime.now().isoformat() + "Z"
        order = shippo.Order.create(**ORDER)
        retrieve = shippo.Order.retrieve(order.object_id)
        self.assertCountEqual(order.object_id, retrieve.object_id)

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/order")
    def test_invalid_retrieve(self):
        self.assertRaises(shippo.error.APIError, shippo.Order.retrieve, "EXAMPLE_OF_INVALID_ID")

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/order")
    def test_list_all(self):
        order_list = shippo.Order.all()
        self.assertTrue("results" in order_list)

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/order")
    def test_list_page_size(self):
        pagesize = 1
        order_list = shippo.Order.all(size=pagesize)
        self.assertEqual(len(order_list.results), pagesize)

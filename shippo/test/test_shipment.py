import shippo
from shippo.test.helper import create_mock_shipment, INVALID_SHIPMENT, ShippoTestCase, shippo_vcr


class ShipmentTests(ShippoTestCase):
    request_client = shippo.http_client.RequestsClient

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/shipment")
    def test_invalid_create(self):
        self.assertRaises(shippo.error.InvalidRequestError, shippo.Shipment.create, **INVALID_SHIPMENT)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/shipment")
    def test_create(self):
        shipment = create_mock_shipment()
        self.assertEqual(shipment.status, "SUCCESS")

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/shipment")
    def test_retrieve(self):
        shipment = create_mock_shipment()
        retrieve = shippo.Shipment.retrieve(shipment.object_id)
        self.assertCountEqual(shipment, retrieve)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/shipment")
    def test_invalid_retrieve(self):
        self.assertRaises(shippo.error.APIError, shippo.Shipment.retrieve, "EXAMPLE_OF_INVALID_ID")

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/shipment")
    def test_list_all(self):
        shipment_list = shippo.Shipment.all()
        self.assertTrue("results" in shipment_list)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/shipment")
    def test_list_page_size(self):
        pagesize = 1
        shipment_list = shippo.Shipment.all(size=pagesize)
        self.assertEqual(len(shipment_list.results), pagesize)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/shipment")
    def test_get_rate(self):
        shipment = create_mock_shipment()
        rates = shippo.Shipment.get_rates(shipment.object_id)
        self.assertTrue("results" in rates)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/shipment")
    def test_get_rates_blocking(self):
        shipment = create_mock_shipment()
        rates = shippo.Shipment.get_rates(shipment.object_id, asynchronous=False)
        self.assertTrue("results" in rates)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/shipment")
    def test_invalid_get_rate(self):
        # we are testing asynchronous=True in order to test the 2nd API call of the function
        self.assertRaises(shippo.error.APIError, shippo.Shipment.get_rates, "EXAMPLE_OF_INVALID_ID", asynchronous=True)

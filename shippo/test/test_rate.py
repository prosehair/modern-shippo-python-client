import shippo
from shippo.test.helper import create_mock_shipment, ShippoTestCase, shippo_vcr


class RateTests(ShippoTestCase):
    request_client = shippo.http_client.RequestsClient

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/rate")
    def test_retrieve(self):
        shipment = create_mock_shipment()
        rates = shippo.Shipment.get_rates(shipment.object_id, asynchronous=False)
        rate = rates.results[0]
        retrieve = shippo.Rate.retrieve(rate.object_id)
        self.assertCountEqual(rate, retrieve)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/rate")
    def test_invalid_retrieve(self):
        self.assertRaises(shippo.error.APIError, shippo.Rate.retrieve, "EXAMPLE_OF_INVALID_ID")

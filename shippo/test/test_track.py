from unittest.mock import patch

import shippo
from shippo.test.helper import ShippoTestCase, shippo_vcr


class TrackTests(ShippoTestCase):
    request_client = shippo.http_client.RequestsClient
    tracking_no = "SHIPPO_TRANSIT"
    carrier_token = "shippo"

    def setUp(self):
        super().setUp()

        def get_http_client(*args, **kwargs):
            return self.request_client(*args, **kwargs)

        self.client_patcher = patch("shippo.http_client.new_default_http_client")

        client_mock = self.client_patcher.start()
        client_mock.side_effect = get_http_client

    def tearDown(self):
        super().tearDown()

        self.client_patcher.stop()

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/track")
    def test_get_status(self):
        tracking = shippo.Track.get_status(self.carrier_token, self.tracking_no)
        self.assertTrue(tracking)
        self.assertTrue("tracking_status" in tracking)
        self.assertTrue("tracking_history" in tracking)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/track")
    def test_invalid_get_status(self):
        with self.assertRaises(shippo.error.InvalidRequestError):
            shippo.Track.get_status("EXAMPLE_OF_INVALID_CARRIER", self.tracking_no)

        with self.assertRaises(shippo.error.InvalidRequestError):
            shippo.Track.get_status(self.carrier_token, "EXAMPLE_OF_INVALID_TRACKING_NUMBER")

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/track")
    def test_create(self):
        tracking = shippo.Track.create(carrier=self.carrier_token, tracking_number=self.tracking_no, metadata="metadata")
        self.assertTrue(tracking)
        self.assertTrue("tracking_status" in tracking)
        self.assertTrue("tracking_history" in tracking)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/track")
    def test_invalid_carrier(self):
        with self.assertRaises(shippo.error.InvalidRequestError):
            shippo.Track.create(carrier="EXAMPLE_OF_INVALID_CARRIER", tracking_number=self.tracking_no, metadata="metadata")

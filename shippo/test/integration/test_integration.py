import os
from unittest import SkipTest
from unittest.mock import patch

import shippo
from shippo.config import config
from shippo.test.helper import (
    create_mock_shipment,
    DUMMY_ADDRESS,
    ShippoTestCase,
)


class FunctionalTests(ShippoTestCase):
    request_client = shippo.http_client.RequestsClient

    @classmethod
    def setUpClass(cls):
        if not os.environ.get("SHIPPO_API_KEY"):
            raise SkipTest("Set your SHIPPO_API_KEY in your os.environ")

    @patch.object(config, "api_base", "https://my-invalid-domain.ireallywontresolve/v1")
    def test_dns_failure(self):
        self.assertRaises(shippo.error.APIConnectionError, shippo.Address.create)

    def test_run(self):
        try:
            address = shippo.Address.create(**DUMMY_ADDRESS)
            self.assertEqual(address.is_complete, True)
            address_validated = shippo.Address.validate(address.object_id)
            self.assertEqual(address_validated.is_complete, True)
        except Exception as inst:
            self.fail(f"Test failed with exception {inst}")

    def test_list_accessors(self):
        address = shippo.Address.create(**DUMMY_ADDRESS)
        self.assertEqual(address["object_created"], address.object_created)
        address["foo"] = "bar"
        self.assertEqual(address.foo, "bar")

    def test_unicode(self):
        # Make sure unicode requests can be sent
        self.assertRaises(shippo.error.APIError, shippo.Address.retrieve, "☃")

    def test_get_rates(self):
        try:
            shipment = create_mock_shipment()
            rates = shippo.Shipment.get_rates(shipment.object_id, asynchronous=False)
        except shippo.error.InvalidRequestError:
            pass
        except Exception as inst:
            self.fail(f"Test failed with exception {inst}")
        self.assertTrue("results" in rates)

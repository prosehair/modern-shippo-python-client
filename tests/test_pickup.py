from datetime import datetime, timedelta

import shippo
from tests.helper import create_mock_international_transaction, ShippoTestCase, DUMMY_PICKUP, shippo_vcr


class PickupTests(ShippoTestCase):
    request_client = shippo.http_client.RequestsClient

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/pickup")
    def test_create(self):
        transaction, carrier_account = create_mock_international_transaction()
        PICKUP = DUMMY_PICKUP
        PICKUP["carrier_account"] = carrier_account
        PICKUP["transactions"] = [transaction.object_id]
        pickupTimeStart = datetime.now() + timedelta(hours=1)
        pickupTimeEnd = pickupTimeStart + timedelta(days=1)
        PICKUP["pickupTimeStart"] = pickupTimeStart.isoformat() + "Z"
        PICKUP["pickupTimeEnd"] = pickupTimeEnd.isoformat() + "Z"
        try:
            pickup = shippo.Pickup.create(**PICKUP)
        except shippo.error.InvalidRequestError:
            self.skipTest("Invalid request error")
        else:
            self.assertEqual(pickup.status, "SUCCESS")

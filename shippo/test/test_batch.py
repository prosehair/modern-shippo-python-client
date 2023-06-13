import unittest

import shippo
from shippo.test.helper import ShippoTestCase, DUMMY_BATCH, INVALID_BATCH, create_mock_shipment, shippo_vcr

BATCH_ADD_SIZE = 4


class BatchTests(ShippoTestCase):
    request_client = shippo.http_client.RequestsClient

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/batch")
    def test_create(self):
        BATCH = DUMMY_BATCH.copy()
        batch = shippo.Batch.create(**BATCH)
        self.assertEqual(batch.status, "VALIDATING")

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/batch")
    def test_invalid_create(self):
        with self.assertRaises(shippo.error.InvalidRequestError):
            shippo.Batch.create()
        INVALID = INVALID_BATCH.copy()
        with self.assertRaises(shippo.error.InvalidRequestError):
            shippo.Batch.create(**INVALID)

    @unittest.skip("Invalid fixture data")
    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/batch")
    def test_retrieve(self):
        BATCH = DUMMY_BATCH.copy()
        batch = shippo.Batch.create(**BATCH)
        retrieve = shippo.Batch.retrieve(batch.object_id)
        self.assertCountEqual(batch, retrieve)
        # Leave enough time for the batch to be processed
        retrieve = shippo.Batch.retrieve(batch.object_id, **{"object_results": "creation_succeeded"})
        self.assertGreater(len(retrieve["batch_shipments"]["results"]), 0)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/batch")
    def test_invalid_retrieve(self):
        with self.assertRaises(shippo.error.APIError):
            shippo.Batch.retrieve("EXAMPLE_OF_INVALID_ID")

    @unittest.skip("Invalid fixture data")
    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/batch")
    def test_add(self):
        BATCH = DUMMY_BATCH.copy()
        batch = shippo.Batch.create(**BATCH)
        # Leave enough time for the batch to be processed
        retrieve = shippo.Batch.retrieve(batch.object_id)
        batch_size = len(retrieve.batch_shipments.results)
        self.assertEqual(batch.status, "VALIDATING")
        addon = []
        for _ in range(BATCH_ADD_SIZE):
            mock_shipment = create_mock_shipment()
            addon.append({"shipment": mock_shipment.object_id})
        added = shippo.Batch.add(batch.object_id, addon)
        added_size = len(added.batch_shipments.results)
        self.assertEqual(batch_size + len(addon), added_size)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/batch")
    def test_invalid_add(self):
        BATCH = DUMMY_BATCH.copy()
        batch = shippo.Batch.create(**BATCH)
        self.assertEqual(batch.status, "VALIDATING")
        mock_shipment = create_mock_shipment()
        with self.assertRaises(shippo.error.APIError):
            shippo.Batch.add("INVALID_OBJECT_KEY", [{"shipment": [mock_shipment]}])

    @unittest.skip("Invalid fixture data")
    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/batch")
    def test_remove(self):
        BATCH = DUMMY_BATCH.copy()
        batch = shippo.Batch.create(**BATCH)
        # Leave enough time for the batch to be processed
        retrieve = shippo.Batch.retrieve(batch.object_id)
        batch_size = len(retrieve.batch_shipments.results)
        self.assertEqual(batch.status, "VALIDATING")
        addon = []
        for _ in range(BATCH_ADD_SIZE):
            mock_shipment = create_mock_shipment()
            addon.append({"shipment": mock_shipment.object_id})
        added = shippo.Batch.add(batch.object_id, addon)
        added_size = len(added.batch_shipments.results)
        self.assertEqual(batch_size + len(addon), added_size)
        to_remove = []
        for shipment in added.batch_shipments.results:
            to_remove.append(shipment.object_id)
        removed = shippo.Batch.remove(batch.object_id, to_remove)
        self.assertEqual(len(removed.batch_shipments.results), 0)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/batch")
    def test_invalid_remove(self):
        BATCH = DUMMY_BATCH.copy()
        batch = shippo.Batch.create(**BATCH)
        self.assertEqual(batch.status, "VALIDATING")
        retrieve = shippo.Batch.retrieve(batch.object_id)
        to_remove = []
        for shipment in retrieve.batch_shipments.results:
            to_remove.append(shipment.object_id)
        with self.assertRaises(shippo.error.APIError):
            shippo.Batch.add("INVALID_OBJECT_KEY", to_remove)

    @unittest.skip("Invalid fixture data")
    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/batch")
    def test_purchase(self):
        BATCH = DUMMY_BATCH.copy()
        batch = shippo.Batch.create(**BATCH)
        while batch.status == "VALIDATING":
            batch = shippo.Batch.retrieve(batch.object_id)
        purchase = shippo.Batch.purchase(batch.object_id)
        self.assertEqual(purchase.status, "PURCHASING")

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/batch")
    def test_invalid_purchase(self):
        with self.assertRaises(shippo.error.APIError):
            shippo.Batch.purchase("INVALID_OBJECT_ID")

import unittest

import shippo
from tests.helper import INVALID_MANIFEST, ShippoTestCase, create_mock_transaction, create_mock_manifest, shippo_vcr


class ManifestTests(ShippoTestCase):
    request_client = shippo.http_client.RequestsClient

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/manifest")
    def test_invalid_create(self):
        self.assertRaises(shippo.error.InvalidRequestError, shippo.Manifest.create, **INVALID_MANIFEST)

    @unittest.skip("Invalid fixture data")
    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/manifest")
    def test_create(self):
        transaction = create_mock_transaction()
        manifest = create_mock_manifest(transaction)
        self.assertEqual(manifest.status, "SUCCESS")
        self.assertEqual(manifest.transactions[0], transaction.object_id)

    @unittest.skip("Invalid fixture data")
    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/manifest")
    def test_retrieve(self):
        manifest = create_mock_manifest()
        retrieve = shippo.Manifest.retrieve(manifest.object_id)
        self.assertCountEqual(manifest, retrieve)

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/manifest")
    def test_invalid_retrieve(self):
        self.assertRaises(shippo.error.APIError, shippo.Manifest.retrieve, "EXAMPLE_OF_INVALID_ID")

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/manifest")
    def test_list_all(self):
        manifest_list = shippo.Manifest.all()
        self.assertTrue("results" in manifest_list)

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/manifest")
    def test_list_page_size(self):
        pagesize = 1
        manifest_list = shippo.Manifest.all(size=pagesize)
        self.assertEqual(len(manifest_list.results), pagesize)

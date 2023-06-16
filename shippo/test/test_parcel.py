import shippo
from shippo.test.helper import (
    DUMMY_PARCEL,
    INVALID_PARCEL,
    ShippoTestCase,
    shippo_vcr,
)


class ParcelTests(ShippoTestCase):
    request_client = shippo.http_client.RequestsClient

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/parcel")
    def test_invalid_create(self):
        self.assertRaises(shippo.error.InvalidRequestError, shippo.Parcel.create, **INVALID_PARCEL)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/parcel")
    def test_create(self):
        parcel = shippo.Parcel.create(**DUMMY_PARCEL)
        self.assertEqual(parcel.object_state, "VALID")

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/parcel")
    def test_retrieve(self):
        parcel = shippo.Parcel.create(**DUMMY_PARCEL)
        retrieve = shippo.Parcel.retrieve(parcel.object_id)
        self.assertCountEqual(parcel, retrieve)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/parcel")
    def test_invalid_retrieve(self):
        self.assertRaises(shippo.error.APIError, shippo.Parcel.retrieve, "EXAMPLE_OF_INVALID_ID")

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/parcel")
    def test_list_all(self):
        parcel_list = shippo.Parcel.all()
        self.assertTrue("results" in parcel_list)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/parcel")
    def test_list_page_size(self):
        pagesize = 2
        parcel_list = shippo.Parcel.all(size=pagesize)
        self.assertEqual(len(parcel_list.results), pagesize)

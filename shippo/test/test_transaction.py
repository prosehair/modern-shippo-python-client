import shippo
from shippo.test.helper import create_mock_shipment, ShippoTestCase, DUMMY_TRANSACTION, shippo_vcr


class TransactionTests(ShippoTestCase):
    request_client = shippo.http_client.RequestsClient

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/transaction")
    def test_invalid_create(self):
        self.assertRaises(shippo.error.InvalidRequestError, shippo.Transaction.create)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/transaction")
    def test_create(self):
        shipment = create_mock_shipment()
        rates = shippo.Shipment.get_rates(shipment.object_id, asynchronous=False)
        rate = rates.results[0]
        TRANSACTION = DUMMY_TRANSACTION.copy()
        TRANSACTION["rate"] = rate.object_id
        transaction = shippo.Transaction.create(**TRANSACTION)
        self.assertEqual(transaction.object_state, "VALID")

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/transaction")
    def test_retrieve(self):
        shipment = create_mock_shipment()
        rates = shippo.Shipment.get_rates(shipment.object_id, asynchronous=False)
        rate = rates.results[0]
        TRANSACTION = DUMMY_TRANSACTION.copy()
        TRANSACTION["rate"] = rate.object_id
        transaction = shippo.Transaction.create(**TRANSACTION)
        retrieve = shippo.Transaction.retrieve(transaction.object_id)
        self.assertCountEqual(transaction, retrieve)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/transaction")
    def test_invalid_retrieve(self):
        self.assertRaises(shippo.error.APIError, shippo.Transaction.retrieve, "EXAMPLE_OF_INVALID_ID")

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/transaction")
    def test_list_all(self):
        transaction_list = shippo.Transaction.all()
        self.assertTrue("results" in transaction_list)

    @shippo_vcr.use_cassette(cassette_library_dir="shippo/test/fixtures/transaction")
    def test_list_page_size(self):
        pagesize = 1
        transaction_list = shippo.Transaction.all(size=pagesize)
        self.assertEqual(len(transaction_list.results), pagesize)

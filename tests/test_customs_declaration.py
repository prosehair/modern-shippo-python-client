import shippo
from tests.helper import DUMMY_CUSTOMS_DECLARATION, INVALID_CUSTOMS_DECLARATION, DUMMY_CUSTOMS_ITEM, ShippoTestCase, shippo_vcr


class CustomsDeclarationTests(ShippoTestCase):
    request_client = shippo.http_client.RequestsClient

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/customs-declaration")
    def test_invalid_create(self):
        self.assertRaises(shippo.error.InvalidRequestError, shippo.CustomsDeclaration.create, **INVALID_CUSTOMS_DECLARATION)

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/customs-declaration")
    def test_create(self):
        customs_item = shippo.CustomsItem.create(**DUMMY_CUSTOMS_ITEM)
        customs_declaration_parameters = DUMMY_CUSTOMS_DECLARATION.copy()
        customs_declaration_parameters["items"][0] = customs_item.object_id
        CustomsDeclaration = shippo.CustomsDeclaration.create(**customs_declaration_parameters)
        self.assertEqual(CustomsDeclaration.object_state, "VALID")

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/customs-declaration")
    def test_retrieve(self):
        customs_item = shippo.CustomsItem.create(**DUMMY_CUSTOMS_ITEM)
        customs_declaration_parameters = DUMMY_CUSTOMS_DECLARATION.copy()
        customs_declaration_parameters["items"][0] = customs_item.object_id
        CustomsDeclaration = shippo.CustomsDeclaration.create(**customs_declaration_parameters)
        # Test Retrieving Object
        retrieve = shippo.CustomsDeclaration.retrieve(CustomsDeclaration.object_id)
        self.assertCountEqual(CustomsDeclaration, retrieve)

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/customs-declaration")
    def test_invalid_retrieve(self):
        self.assertRaises(shippo.error.APIError, shippo.CustomsDeclaration.retrieve, "EXAMPLE_OF_INVALID_ID")

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/customs-declaration")
    def test_list_all(self):
        customs_declaration_list = shippo.CustomsDeclaration.all()
        self.assertTrue("results" in customs_declaration_list)

    @shippo_vcr.use_cassette(cassette_library_dir="tests/fixtures/customs-declaration")
    def test_list_page_size(self):
        pagesize = 1
        customs_declaration_list = shippo.CustomsDeclaration.all(size=pagesize)
        self.assertEqual(len(customs_declaration_list.results), pagesize)

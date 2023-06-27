import sys
from unittest.mock import Mock, patch

from requests.exceptions import RequestException

from shippo import http_client
from shippo.config import config, Configuration
from shippo.error import APIConnectionError
from tests.helper import ShippoTestCase


class ShippoAuthTest(ShippoTestCase):
    def test_oauth_token_auth(self):
        api_key = "oauth.mocktoken.mocksig"
        auth = http_client.ShippoAuth(api_key)
        mock_request = Mock()
        mock_request.headers = {}
        actual = auth(mock_request)
        self.assertEqual(actual.headers["Authorization"], f"Bearer {api_key}", "Expect correct token type to used for authorization with oauth token")

    def test_shippo_token_auth(self):
        api_key = "shippo_test_mocktoken"
        auth = http_client.ShippoAuth(api_key)
        mock_request = Mock()
        mock_request.headers = {}
        actual = auth(mock_request)
        self.assertEqual(
            actual.headers["Authorization"], f"ShippoToken {api_key}", "Expect correct token type to used for authorization with shippo token"
        )


class RequestsClientTests(ShippoTestCase):
    valid_url = "https://api.goshippo.com/v1/echo"

    @patch.object(sys, "version", "3.8.1 (default, Mar 13 2020, 20:31:03) \n[Clang 11.0.0 (clang-1100.0.33.17)]")
    def test_shippo_user_agent(self):
        configuration = Configuration()
        configuration.app_name = "TestApp"
        configuration.app_version = "1.1.1"
        configuration.sdk_version = "0.0.0"

        actual = http_client._get_shippo_user_agent_header(configuration=configuration)
        expected = "TestApp/1.1.1 ShippoPythonSDK/0.0.0 Python/3.8.1"
        self.assertEqual(actual, expected)

    def test_http_client_init(self):
        with self.assertRaises(ValueError):
            http_client.RequestsClient(verify_ssl_certs=None)

    def test_default_timeout(self):
        with patch("requests.Session.request") as mock:
            client = http_client.RequestsClient()
            client.request(url=self.valid_url)
            mock.assert_called_with(url=self.valid_url, timeout=config.default_timeout)

    def test_custom_timeout(self):
        timeout = config.default_timeout + 1  # Make sure we test over a different value than the default

        with patch("requests.Session.request") as mock:
            client = http_client.RequestsClient()
            client.request(url=self.valid_url, timeout=timeout)
            mock.assert_called_with(url=self.valid_url, timeout=timeout)

    def test_error_handling(self):
        with patch("requests.Session.request", side_effect=RequestException("test")):
            client = http_client.RequestsClient()
            with self.assertRaises(APIConnectionError):
                client.request(url=self.valid_url)

        with patch("requests.Session.request", side_effect=KeyError("test")):
            client = http_client.RequestsClient()
            with self.assertRaises(APIConnectionError):
                client.request(url=self.valid_url)

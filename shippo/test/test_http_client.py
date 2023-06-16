from unittest.mock import patch

from requests.exceptions import RequestException

import shippo
from shippo.test.helper import ShippoTestCase


class RequestsClientTests(ShippoTestCase):
    valid_url = "https://api.goshippo.com/v1/echo"

    def test_init(self):
        with self.assertRaises(ValueError):
            shippo.http_client.RequestsClient(verify_ssl_certs=None)

    def test_default_timeout(self):
        with patch("requests.Session.request") as mock:
            client = shippo.http_client.RequestsClient()
            client.request(url=self.valid_url)
            mock.assert_called_with(url=self.valid_url, timeout=shippo.http_client.DEFAULT_TIMEOUT)

    def test_custom_timeout(self):
        timeout = shippo.http_client.DEFAULT_TIMEOUT + 1  # Make sure we test over a different value than the default

        with patch("requests.Session.request") as mock:
            client = shippo.http_client.RequestsClient()
            client.request(url=self.valid_url, timeout=timeout)
            mock.assert_called_with(url=self.valid_url, timeout=timeout)

    def test_error_handling(self):
        with patch("requests.Session.request", side_effect=RequestException("test")):
            client = shippo.http_client.RequestsClient()
            with self.assertRaises(shippo.error.APIConnectionError):
                client.request(url=self.valid_url)

        with patch("requests.Session.request", side_effect=KeyError("test")):
            client = shippo.http_client.RequestsClient()
            with self.assertRaises(shippo.error.APIConnectionError):
                client.request(url=self.valid_url)

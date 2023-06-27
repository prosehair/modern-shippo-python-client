"""
- Requests is the preferred HTTP library
- Google App Engine has urlfetch, we use request_toolbelt to monkey patch and keep the same signature
"""
import sys
import textwrap

from requests import Session
from requests.auth import AuthBase
from requests.exceptions import RequestException

from shippo import error
from shippo.config import config, Configuration


def _get_shippo_user_agent_header(configuration: Configuration) -> str:
    python_version = sys.version.split(" ", maxsplit=1)[0]
    key_value_pairs = []
    key_value_pairs.append("/".join([configuration.app_name, configuration.app_version]))
    key_value_pairs.append("/".join([configuration.sdk_name, configuration.sdk_version]))
    key_value_pairs.append("/".join([configuration.language, python_version]))
    return " ".join(key_value_pairs)


class ShippoAuth(AuthBase):
    def __init__(self, api_key=None):
        self.api_key = api_key or config.api_key
        self.token_type = "Bearer" if self.api_key.startswith("oauth.") else "ShippoToken"

    def __call__(self, r):
        r.headers["Authorization"] = f"{self.token_type} {self.api_key}"
        return r


class RequestsClient(Session):
    def __init__(self, api_key=None, verify_ssl_certs=True, timeout=None):
        super().__init__()
        if verify_ssl_certs is None:
            raise ValueError("`verify_ssl_certs` cannot be None")
        self.auth = ShippoAuth(api_key)
        self.verify = verify_ssl_certs
        self._set_default_headers()

    def _set_default_headers(self):
        self.headers = self.headers or {}
        self.headers.update(
            {
                "Content-Type": "application/json",
                "X-Shippo-Client-User-Agent": _get_shippo_user_agent_header(config),
                "User-Agent": f"{config.app_name}/{config.app_version} ShippoPythonSDK/{config.sdk_version}",
                "Shippo-API-Version": config.api_version,
            }
        )

    def request(self, *args, timeout=None, **kwargs):
        timeout = timeout or config.default_timeout
        try:
            response = super().request(*args, timeout=timeout, **kwargs)
        except Exception as err:
            if isinstance(err, RequestException):
                msg = "Unexpected error communicating with Shippo. If this problem persists, let us know at support@goshippo.com."
            else:
                msg = (
                    "Unexpected error communicating with Shippo. "
                    "It looks like there's probably a configuration "
                    "issue locally.  If this problem persists, let us "
                    "know at support@goshippo.com."
                )
            details = f"{type(err).__name__}: {err}"
            msg = textwrap.fill(msg) + f"\n\n(Network error: {details})"
            raise error.APIConnectionError(msg)

        return response.text, response.status_code

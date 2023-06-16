"""
- Requests is the preferred HTTP library
- Google App Engine has urlfetch, we use request_toolbelt to monkey patch and keep the same signature
"""
import textwrap

from requests import Session
from requests.exceptions import RequestException

from shippo import error

DEFAULT_TIMEOUT = 80

try:
    import requests_toolbelt.adapters.appengine
except ImportError:
    pass
else:
    requests_toolbelt.adapters.appengine.monkeypatch()
    DEFAULT_TIMEOUT = 55


class RequestsClient(Session):
    def __init__(self, verify_ssl_certs=True, timeout_in_seconds=None):
        super().__init__()
        if verify_ssl_certs is None:
            raise ValueError("`verify_ssl_certs` cannot be None")
        self.verify = verify_ssl_certs

    def request(self, *args, timeout=None, **kwargs):
        timeout = timeout or DEFAULT_TIMEOUT
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

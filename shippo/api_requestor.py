import calendar
import datetime
import json
import logging
import time
import urllib.parse
import warnings

from shippo import error, http_client
from shippo.config import config

logger = logging.getLogger(__name__)


def urljoin(base, *parts):
    *parts, last_part = parts
    stripped_parts = (part.strip("/") for part in parts)
    return "/".join((base.rstrip("/"), *stripped_parts, last_part.lstrip("/")))


def _encode_datetime(dttime):
    if dttime.tzinfo and dttime.tzinfo.utcoffset(dttime) is not None:
        utc_timestamp = calendar.timegm(dttime.utctimetuple())
    else:
        utc_timestamp = time.mktime(dttime.timetuple())

    return int(utc_timestamp)


def _api_encode(data):
    for key, value in data.items():
        if value is None:
            continue
        if hasattr(value, "shippo_id"):
            yield key, value.shippo_id
        elif isinstance(value, (list, tuple)):
            for subvalue in value:
                yield f"{key}[]", subvalue
        elif isinstance(value, dict):
            subdict = {f"{key}[{subkey}]": subvalue for subkey, subvalue in value.items()}
            for subkey, subvalue in _api_encode(subdict):
                yield subkey, subvalue
        elif isinstance(value, datetime.datetime):
            yield key, _encode_datetime(value)
        else:
            yield key, value


def _build_api_url(url, query):
    scheme, netloc, path, base_query, fragment = urllib.parse.urlsplit(url)
    if base_query:
        query = f"{base_query}&{query}"
    return urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))


class APIRequestor:
    def __init__(self, api_key=None, client=None, **kwargs):
        if "key" in kwargs:
            warnings.warn("key parameter has been renamed to api_key", DeprecationWarning)
            if api_key:
                raise ValueError("key parameter is deprecated, and cannot be used with api_key")
            api_key = kwargs.pop("key")

        self._client = client or http_client.RequestsClient(api_key=api_key, verify_ssl_certs=config.verify_ssl_certs, timeout=config.default_timeout)

    def request(self, method, url, params=None):
        if isinstance(params, dict) and "asynchronous" in params:
            params["async"] = params.pop("asynchronous")

        rbody, rcode = self.request_raw(method.lower(), url, params)
        resp = self.interpret_response(rbody, rcode)
        return resp

    def handle_api_error(self, rbody, rcode, resp):
        if rcode in (400, 404):
            raise error.InvalidRequestError(rbody, rcode, resp)
        if rcode == 401:
            raise error.AuthenticationError(rbody, rcode, resp)
        raise error.APIError(rbody, rcode, resp)

    def request_raw(self, method, url, params=None):
        """
        Mechanism for issuing an API call
        """
        abs_url = urljoin(config.api_base, url)

        if method.lower() in ("get", "delete"):
            if params:
                encoded_params = urllib.parse.urlencode(list(_api_encode(params or {})))
                abs_url = _build_api_url(abs_url, encoded_params)
            post_data = None
        elif method in ("post", "put"):
            post_data = json.dumps(params)
        else:
            raise error.APIConnectionError(
                f"Unrecognized HTTP method {method!r}.  This may indicate a bug in the "
                "Shippo bindings.  Please contact support@goshippo.com for "
                "assistance."
            )

        rbody, rcode = self._client.request(method=method, url=abs_url, data=post_data)
        logger.info("API request to %s returned (response code, response body) of (%d, %s)", abs_url, rcode, rbody)
        return rbody, rcode

    def interpret_response(self, rbody, rcode):
        try:
            if rbody == "":
                rbody = '{"msg": "empty_response"}'
            resp = json.loads(rbody)
        except Exception as err:
            raise error.APIError(f"Invalid response body from API: {rbody} (HTTP response code was {rcode})", rbody, rcode) from err
        if not 200 <= rcode < 300:
            self.handle_api_error(rbody, rcode, resp)
        return resp

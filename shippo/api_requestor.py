import calendar
import datetime
import json
import logging
import time
import urllib.parse
import sys
from shippo import error, http_client
from shippo.config import config, Configuration

logger = logging.getLogger(__name__)


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
    def __init__(self, key=None, client=None):
        self.api_key = key

        self._client = client or http_client.RequestsClient(verify_ssl_certs=config.verify_ssl_certs, timeout_in_seconds=config.timeout_in_seconds)

    def request(self, method, url, params=None):
        if params is not None and isinstance(params, dict):
            params = {("async" if k == "asynchronous" else k): v for k, v in params.items()}

        rbody, rcode, my_api_key = self.request_raw(method.lower(), url, params)

        resp = self.interpret_response(rbody, rcode)
        return resp, my_api_key

    def handle_api_error(self, rbody, rcode, resp):
        if rcode in (400, 404):
            raise error.InvalidRequestError(rbody, rcode, resp)
        if rcode == 401:
            raise error.AuthenticationError(rbody, rcode, resp)
        raise error.APIError(rbody, rcode, resp)

    @staticmethod
    def get_python_version() -> str:
        return sys.version.split(" ", maxsplit=1)[0]

    @staticmethod
    def get_shippo_user_agent_header(configuration: Configuration) -> str:
        key_value_pairs = []
        key_value_pairs.append("/".join([configuration.app_name, configuration.app_version]))
        key_value_pairs.append("/".join([configuration.sdk_name, configuration.sdk_version]))
        key_value_pairs.append("/".join([configuration.language, APIRequestor.get_python_version()]))
        return " ".join(key_value_pairs)

    def request_raw(self, method, url, params=None):
        """
        Mechanism for issuing an API call
        """

        if self.api_key:
            my_api_key = self.api_key
        else:
            my_api_key = config.api_key

        if my_api_key is None:
            raise error.AuthenticationError(
                "No API key provided. (HINT: set your API key using "
                '"shippo.config.api_key = shippo_test_d90f00698a0a8def0495fddb4212bb08051469d3"). You can generate API keys '
                "from the Shippo web interface.  See https://goshippo.com/api "
                "for details, or email support@goshippo.com if you have any "
                "questions."
            )

        token_type = "ShippoToken"
        if my_api_key.startswith("oauth."):
            token_type = "Bearer"

        abs_url = f"{config.api_base}{url}"

        if method in ("get", "delete"):
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

        shippo_user_agent = APIRequestor.get_shippo_user_agent_header(config)

        headers = {
            "Content-Type": "application/json",
            "X-Shippo-Client-User-Agent": shippo_user_agent,
            "User-Agent": f"{config.app_name}/{config.app_version} ShippoPythonSDK/{config.sdk_version}",
            "Authorization": f"{ token_type } {my_api_key}",
            "Shippo-API-Version": config.api_version,
        }

        rbody, rcode = self._client.request(method=method, url=abs_url, headers=headers, data=post_data)
        logger.info("API request to %s returned (response code, response body) of (%d, %s)", abs_url, rcode, rbody)
        return rbody, rcode, my_api_key

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

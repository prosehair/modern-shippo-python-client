import json
import urllib.parse
import time
import warnings
from shippo import api_requestor, error
from shippo.api_requestor import urljoin
from shippo.config import config


warnings.filterwarnings("always", category=DeprecationWarning, module="shippo")


def convert_to_shippo_object(resp):
    if isinstance(resp, list):
        return [convert_to_shippo_object(i) for i in resp]
    if isinstance(resp, dict) and not isinstance(resp, ShippoObject):
        resp = resp.copy()
        return ShippoObject.construct_from(resp)
    return resp


class ShippoObject(dict):
    def __init__(self, id=None, **params):
        super().__init__()

        self._unsaved_values = set()
        self._transient_values = set()

        self._retrieve_params = params
        self._previous_metadata = None

        if id:
            self["object_id"] = id

    def __setattr__(self, k, v):
        if k[0] == "_" or k in self.__dict__:
            super().__setattr__(k, v)
        else:
            self[k] = v

    def __getattr__(self, k):
        if k[0] == "_":
            raise AttributeError(k)

        try:
            return self[k]
        except KeyError as err:
            raise AttributeError(*err.args) from err

    def __setitem__(self, k, v):
        if v == "":
            raise ValueError(
                f"You cannot set {k} to an empty string. "
                "We interpret empty strings as None in requests."
                f"You may set {str(self)}.{k} = None to delete the property"
            )

        super().__setitem__(k, v)

        # Allows for unpickling in Python 3.x
        if not hasattr(self, "_unsaved_values"):
            self._unsaved_values = set()

        self._unsaved_values.add(k)

    def __getitem__(self, k):
        try:
            return super().__getitem__(k)
        except KeyError as err:
            if k in self._transient_values:
                avail_attrs = ", ".join(list(self.keys()))
                raise KeyError(
                    f"{k!r}.  HINT: The {k!r} attribute was set in the past."
                    "It was then wiped when refreshing the object with "
                    "the result returned by Shippo's API, probably as a "
                    "result of a save().  The attributes currently "
                    f"available on this object are: {avail_attrs}"
                ) from err
            raise err

    def __delitem__(self, k):
        raise TypeError("You cannot delete attributes on a ShippoObject  To unset a property, set it to None.")

    @classmethod
    def construct_from(cls, values):
        instance = cls(id=values.get("object_id"))
        instance.refresh_from(values)
        return instance

    def refresh_from(self, values, partial=False):
        # Wipe old state before setting new.
        if partial:
            self._unsaved_values = self._unsaved_values - set(values)
        else:
            removed = set(self.keys()) - set(values)
            self._transient_values = self._transient_values | removed
            self._unsaved_values = set()

            self.clear()

        self._transient_values = self._transient_values - set(values)

        for k, v in list(values.items()):
            super().__setitem__(k, convert_to_shippo_object(v))

        self._previous_metadata = values.get("metadata")

    def request(self, method, url, params=None):
        if params is None:
            params = self._retrieve_params

        requestor = api_requestor.APIRequestor()
        response = requestor.request(method=method, url=url, params=params)

        return convert_to_shippo_object(response)

    def __repr__(self):
        ident_parts = [type(self).__name__]

        if isinstance(self.get("object"), str):
            ident_parts.append(self.get("object"))

        if isinstance(self.get("object_id"), str):
            ident_parts.append(f"object_id={self.get('object_id')}")

        ident_parts = " ".join(ident_parts)
        return f"<{ident_parts} at {hex(id(self))}> JSON: {self}"

    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2)

    @property
    def shippo_id(self):
        return self.id


class APIResource(ShippoObject):
    def refresh(self):
        self.refresh_from(self.request(method="get", url=self.instance_url()))
        return self

    @classmethod
    def class_name(cls):
        if cls == APIResource:
            raise NotImplementedError("APIResource is an abstract class. You should perform actions on its subclasses (e.g. Address, Parcel)")
        return str(urllib.parse.quote_plus(cls.__name__.lower()))

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return f"{cls_name}s"

    def instance_url(self):
        object_id = self.get("object_id")
        if not object_id:
            raise error.InvalidRequestError(
                f"Could not determine which URL to request: {type(self).__name__} instance has invalid ID: {object_id!r}", "object_id"
            )
        base = self.class_url()
        extn = urllib.parse.quote_plus(object_id)
        return f"{base}/{extn}"


class CreateableAPIResource(APIResource):
    @classmethod
    def create(cls, **params):
        url = cls.class_url()
        requestor = api_requestor.APIRequestor()
        response = requestor.request(method="post", url=url, params=params)
        return convert_to_shippo_object(response)


class ListableAPIResource(APIResource):
    @classmethod
    def all(cls, size=None, page=None, **params):
        """
        To retrieve a list of all the objects in a class. The size of page and
            the page number can be specified respectively cls.all(<size>,<page>)
            **NOTE: To specify a page number, the page size must also be provided
        """
        url = cls.class_url()
        if size:
            params["results"] = str(size)
        if page:
            params["page"] = str(page)
        requestor = api_requestor.APIRequestor()
        response = requestor.request(method="get", url=url, params=params)
        return convert_to_shippo_object(response)


class FetchableAPIResource(APIResource):
    @classmethod
    def retrieve(cls, object_id):
        extn = urllib.parse.quote_plus(object_id)
        url = urljoin(cls.class_url(), extn)
        requestor = api_requestor.APIRequestor()
        response = requestor.request(method="get", url=url)
        return convert_to_shippo_object(response)


class UpdateableAPIResource(APIResource):
    @classmethod
    def update(cls, object_id, **params):
        extn = urllib.parse.quote_plus(object_id)
        url = urljoin(cls.class_url(), extn)
        requestor = api_requestor.APIRequestor()
        response = requestor.request(method="put", url=url, params=params)
        return convert_to_shippo_object(response)

    @classmethod
    def remove(cls, object_id, **params):
        extn = urllib.parse.quote_plus(object_id)
        url = urljoin(cls.class_url(), extn)
        requestor = api_requestor.APIRequestor()
        requestor.request(method="delete", url=url, params=params)
        return "Deleted the webhook"


# ---- API objects ----


class Address(CreateableAPIResource, ListableAPIResource, FetchableAPIResource):
    @classmethod
    def validate(cls, object_id):
        extn = urllib.parse.quote_plus(object_id)
        url = urljoin(cls.class_url(), extn, "/validate")
        requestor = api_requestor.APIRequestor()
        response = requestor.request(method="get", url=url)
        return convert_to_shippo_object(response)

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return f"{cls_name}es/"


class CustomsItem(CreateableAPIResource, ListableAPIResource, FetchableAPIResource):
    @classmethod
    def class_url(cls):
        return "customs/items/"


class CustomsDeclaration(CreateableAPIResource, ListableAPIResource, FetchableAPIResource):
    @classmethod
    def class_url(cls):
        return "customs/declarations/"


class Parcel(CreateableAPIResource, ListableAPIResource, FetchableAPIResource):
    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return f"{cls_name}s/"


class Pickup(CreateableAPIResource):
    """
    A Pickup allows you to schedule pickups with USPS and DHL Express for eligible shipments that you have already created.
    """

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return f"{cls_name}s/"


class Manifest(CreateableAPIResource, ListableAPIResource, FetchableAPIResource):
    """
    Manifests are close-outs of shipping labels of a certain day. Some carriers
       require Manifests to properly process the shipments
    """

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return f"{cls_name}s/"


class Refund(CreateableAPIResource, ListableAPIResource, FetchableAPIResource):
    """
    Refunds are reimbursements for successfully created but unused Transaction.
    """

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return f"{cls_name}s/"


class Shipment(CreateableAPIResource, ListableAPIResource, FetchableAPIResource):
    """
    The heart of the Shippo API, a Shipment is made up of "to" and "from" Addresses
    and the Parcel to be shipped. Shipments can be created, retrieved and listed.
    """

    @classmethod
    def get_rates(cls, object_id, asynchronous=False, currency=None, **params):
        """
        Given a valid shipment object_id, all possible rates are calculated and returned.
        """
        if not asynchronous:
            timeout = time.time() + config.rates_req_timeout
            while cls.retrieve(object_id).status in ("QUEUED", "WAITING") and time.time() < timeout:
                continue

        shipment_id = urllib.parse.quote_plus(object_id)
        url = urljoin(cls.class_url(), shipment_id, "/rates/")
        if currency:
            url = urljoin(url, urllib.parse.quote_plus(currency))
        requestor = api_requestor.APIRequestor()
        response = requestor.request(method="get", url=url)
        return convert_to_shippo_object(response)

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return f"{cls_name}s/"


class Transaction(CreateableAPIResource, ListableAPIResource, FetchableAPIResource):
    """
    A Transaction is the purchase of a Shipment Label for a given Shipment Rate.
    Transactions can be as simple as posting a Rate ID.
    """

    @classmethod
    def create(cls, **params):
        """
        Creates a new transaction object, given a valid rate ID.
        Takes the parameters as a dictionary instead of key word arguments.
        """
        # will be removed in the next major version
        return super().create(**params)

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return f"{cls_name}s/"


class Rate(ListableAPIResource, FetchableAPIResource):
    """
    Each valid Shipment object will automatically trigger the calculation of all available
    Rates. Depending on your Addresses and Parcel, there may be none, one or multiple Rates
    """

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return f"{cls_name}s/"


class CarrierAccount(CreateableAPIResource, ListableAPIResource, FetchableAPIResource, UpdateableAPIResource):
    @classmethod
    def class_url(cls):
        return "carrier_accounts/"


class Webhook(CreateableAPIResource, ListableAPIResource, FetchableAPIResource, UpdateableAPIResource):
    """
    retrieve, update and delete webhooks for a Shippo account programmatically.
    The same functionality is already exposed in the Shippo dashboard at https://app.goshippo.com/api/.

    To add both a webhook and track a url at the same see the shippo.Track.create function.
    """

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return f"{cls_name}s/"

    @classmethod
    def list_webhooks(cls, **params):
        """List all the webhooks associated with the account"""
        return super().all(**params)

    @classmethod
    def create(cls, **params):
        """Create a Webhook to push events from Shippo (i.e tracking,transations)

        Arguments:
            **params
                url (str) -- url of your webhook (make sure it is not behind basic auth.
                                  endpoint must return 200 when it receives a POST
                event (str) -- any valid webhook event as listed here https://goshippo.com/docs/webhooks.
                is_test (str) -- set the webhook object to test or live mode

        Returns:
            (ShippoObject) -- The server response
        """

        return super().create(**params)

    @classmethod
    def update_webhook(cls, object_id, **params):
        """
        Update webhook's url, is_test, and/or event
        """
        return super().update(**params)

    @classmethod
    def delete(cls, object_id, **params):
        """Remove webhook

        Arguments:
            object_id (str) -- object_id of webhook

        Returns:
            (ShippoObject) -- The server response
        """
        return super().remove(object_id, **params)


class Track(CreateableAPIResource):
    """
    A Track object gives you the current shipping state of a package not tendered through Shippo
    given a carrier and respective tracking number. It also allows you to register a webhook to
    a carrier + tracking number pair in order to receive live updates.

    Tracking packages tendered through Shippo can be done through the Transaction object
    """

    @classmethod
    def get_status(cls, carrier_token, tracking_number):
        """
        A custom get method for tracking based on carrier and tracking number
        Written because the endpoint for tracking is different from our standard endpoint

        Arguments:
            carrier_token (str) -- name of the carrier of the shipment to track
                                    see https://goshippo.com/docs/reference#carriers
            tracking_number (str) -- tracking number to track

        Returns:
            (ShippoObject) -- The server response
        """
        carrier_token = urllib.parse.quote_plus(carrier_token)
        tracking_number = urllib.parse.quote_plus(tracking_number)
        url = urljoin(cls.class_url(), carrier_token, tracking_number)
        requestor = api_requestor.APIRequestor()
        response = requestor.request(method="get", url=url)
        return convert_to_shippo_object(response)

    @classmethod
    def create(cls, **params):
        """
        Creates a webhook to keep track of the shipping status of a specific package

        Arguments:
            **params
                carrier (str) -- name of the carrier of the shipment to track
                                  see https://goshippo.com/docs/reference#carriers
                tracking_number (str) -- tracking number to track
                metadata (str) -- A string of up to 100 characters that can be filled with any
                                   additional information you want to attach to the object

        Returns:
            (ShippoObject) -- The server response
        """
        return super().create(**params)

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return f"{cls_name}s/"


class Batch(CreateableAPIResource, FetchableAPIResource):
    """
    A Batch bundles together large amounts of shipments, up to 10,000
    """

    @classmethod
    def retrieve(cls, object_id, **params):
        """
        Retrieve a batch, customized to allow the addition of url parameters

        Arguments:
            object_id (str) -- the batch object id
            **params
                page (int as str) -- pagination
                object_results (str) -- valid options are:
                                            "creation_failed"
                                            "creation_succeeded"
                                            "purchase_succeeded"
                                            "purchase_failed"

        Returns:
            (ShippoObject) -- The server response
        """
        url = urljoin(cls.class_url(), urllib.parse.quote_plus(object_id))
        requestor = api_requestor.APIRequestor()
        response = requestor.request(method="get", url=url, params=params)
        return convert_to_shippo_object(response)

    @classmethod
    def add(cls, object_id, shipments_to_add):
        """
        Add shipments to a batch

        Arguments:
            object_id (str) -- the batch object id
            shipments_to_add (list of dict) -- list of shipments to add, must be in the format
                [{'shipment': <shipment 1 object id>}, {'shipment': <shipment 2 object id>}, ...]

        Returns:
            (ShippoObject) -- The server response
        """
        extn = urllib.parse.quote_plus(object_id)
        url = urljoin(cls.class_url(), extn, "/add_shipments")
        requestor = api_requestor.APIRequestor()
        response = requestor.request(method="post", url=url, params=shipments_to_add)
        return convert_to_shippo_object(response)

    @classmethod
    def remove(cls, object_id, shipments_to_remove):
        """
        Remove shipments from a batch

        Arguments:
            object_id (str) -- the batch object id
            shipments_to_remove (list of str) -- list of shipments to remove, must be in the format
                [<shipment 1 object id>, <shipment 2 object id>, ...]

        Returns:
            (ShippoObject) -- The server response
        """
        extn = urllib.parse.quote_plus(object_id)
        url = urljoin(cls.class_url(), extn, "/remove_shipments")
        requestor = api_requestor.APIRequestor()
        response = requestor.request(method="post", url=url, params=shipments_to_remove)
        return convert_to_shippo_object(response)

    @classmethod
    def purchase(cls, object_id):
        """
        Purchase batch of shipments

        Arguments:
            object_id (str) -- the batch object id

        Returns:
            (ShippoObject) -- The server response
        """
        extn = urllib.parse.quote_plus(object_id)
        url = urljoin(cls.class_url(), extn, "/purchase")
        requestor = api_requestor.APIRequestor()
        response = requestor.request(method="post", url=url)
        return convert_to_shippo_object(response)

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return f"{cls_name}es/"


class Order(CreateableAPIResource, ListableAPIResource, FetchableAPIResource):
    """
    Beta functionality, but useful for tracking a given order, label information, etc.
    """

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return f"{cls_name}s/"


class LineItem(ListableAPIResource, FetchableAPIResource):
    """
    Currently this is a nested item inside an Order object.
    """

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return f"{cls_name}s/"

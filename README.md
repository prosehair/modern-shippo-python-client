# Shippo API Python wrapper

Modern [Shippo](https://goshippo.com) API client implementation.

> This implementation is not maintained by Shippo, and is a modern rewrite of their Python client.
> Shippo's documentation specifies that their default implementation is not actively maintained and could be
> used as a starting point if required. (see https://docs.goshippo.com/docs/guides_general/clientlibraries/)
> The goal of this project is to fix some issues with the default implementation (mostly obsolete dependencies).
> We would be happy with the Shippo team taking over this repository and officially maintain it.


## About Shippo

Connect with multiple different carriers, get discounted shipping labels, track parcels, and much more with just one integration.
You can use your own carrier accounts or take advantage of Shippo's discounted rates with the USPS and DHL Express.
Using Shippo makes it easy to deal with multiple carrier integrations, rate shopping, tracking and other parts of the shipping workflow.
Shippo provide the API and dashboard for all your shipping needs.

You will first need to [register for a Shippo account](https://goshippo.com/) to use our API. It's free to sign up, free to use the API. Only pay to print a live label, test labels are free.

### Shippo API Documentation

Please see [https://goshippo.com/docs](https://goshippo.com/docs) for complete up-to-date documentation.

### Supported Shippo Features

The Shippo API provides in depth support of carrier and shipping functionalities. Here are just some of the features we support through the API:

- Shipping rates & labels - [Docs](https://goshippo.com/docs/first-shipment)
- Tracking for any shipment with just the tracking number - [Docs](https://goshippo.com/docs/tracking)
- Batch label generation - [Docs](https://goshippo.com/docs/batch)
- Multi-piece shipments - [Docs](https://goshippo.com/docs/multipiece)
- Manifests and SCAN forms - [Docs](https://goshippo.com/docs/manifests)
- Customs declaration and commercial invoicing - [Docs](https://goshippo.com/docs/international)
- Address verification - [Docs](https://goshippo.com/docs/address-validation)
- Consolidator support including:
  - DHL eCommerce
  - UPS Mail Innovations
  - FedEx Smartpost
- Additional services: cash-on-delivery, certified mail, delivery confirmation, and more - [Docs](https://goshippo.com/docs/reference#shipment-extras)


## How to use

```bash
pip install modern-shippo
```

```python
import shippo

shippo.config.api_key = "<API-KEY>"

address1 = shippo.Address.create(
    name='John Smith',
    street1='6512 Greene Rd.',
    street2='',
    company='Initech',
    phone='+1 234 346 7333',
    city='Woodridge',
    state='IL',
    zip='60517',
    country='US',
    metadata='Customer ID 123456'
)

print(f'Success with Address 1: {address1!r}')
```

We've created a number of examples to cover the most common use cases. You can find the sample code files in the [examples folder](examples/).
Some of the use cases we covered include:

- [Basic domestic shipment](examples/basic-shipment.py)
- [International shipment](examples/international-shipment.py) - Custom forms, interntational destinations
- [Price estimation matrix](examples/estimate-shipping-prices.py)
- [Retrieve rates, filter by delivery time and purchase cheapest label](examples/filter-by-delivery-time.py)
- [Retrieve rates, purchase label for fastest delivery option](examples/purchase-fastest-service.py)
- [Retrieve rates so customer can pick preferred shipping method, purchase label](examples/get-rates-to-show-customer.py)


### Configuration

```python
import shippo

shippo.config.api_key = "<API-KEY>"
shippo.config.api_version = "2018-02-08"
shippo.config.verify_ssl_certs = True
shippo.config.rates_req_timeout = 30.0
shippo.config.default_timeout = 80

shippo.config.app_name = "Name of your Application" # Not required
shippo.config.app_version = "Version of Application" # Not required
```

> Configuration is read from the environement with the SHIPPO_ prefix
> See shippo/config.py for details.

### Use with Google AppEngine

Google AppEngine applications should use UrlFetch to perform HTTP requests.
The Requests module can be monkey-patched to use this HTTP client.
The modern-shippo API client checks for requests_toolbelt availability and properly monkey-patch Requests.

```shell
pip install requests_toolbelt
```

```python
import shippo
import requests_toolbelt.adapters.appengine

requests_toolbelt.adapters.appengine.monkeypatch()
shippo.config.default_timeout = 55  # AppEngine timeout is 60s
```

> This was supported by the original Shippo client implementation, with a much complex http client abstraction.
> Modern-shippo relies entirely on Python Requests to greatly simplify the code base, and rely on requests-toolbelt
> to still support AppEngine.


## How to setup a development environment

Make sure an Python 3.10+ interpretor is installed and available.

Install [hatchling](https://hatch.pypa.io/) to manage environments, run scripts and build the library.

```bash
pip install hatch
```

With hatchling installed, use the integrated CLI to manage environments, run tests and more:

```shell
hatch run test
hatch run lint:style
```

Available environments and commands are available with:

```shell
hatch env show
```

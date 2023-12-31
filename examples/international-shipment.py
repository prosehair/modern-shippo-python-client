"""
In this tutorial we have an order with a sender address,
recipient address and parcel. The shipment is going from the
United States to an international location.

In addition to that we know that the customer expects the
shipment to arrive within 3 days. We now want to purchase
the cheapest shipping label with a transit time <= 3 days.
"""

import shippo

# replace <API-KEY> with your key
shippo.config.api_key = "<API-KEY>"

# Example address_from object dict
# The complete reference for the address object is available here: https://goshippo.com/docs/reference#addresses
address_from = {
    "company": "",
    "street_no": "",
    "name": "Mr. Hippo",
    "street1": "215 Clayton St.",
    "street2": "",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94117",
    "country": "US",
    "phone": "+15553419393",
    "email": "support@goshippo.com",
}

# Example address_to object dict
# The complete reference for the address object is available here: https://goshippo.com/docs/reference#addresses

address_to_international = {
    "name": "Mrs. Hippo",
    "street1": "200 University Ave W",
    "street2": "",
    "city": "Waterloo",
    "state": "ON",
    "zip": "N2L 3G1",
    "country": "CA",
    "phone": "+1 555 341 9393",
    "email": "support@goshippo.com",
    "metadata": "For Order Number 123",
}

# parcel object dict
# The complete reference for parcel object is here: https://goshippo.com/docs/reference#parcels
parcel = {
    "length": "5",
    "width": "5",
    "height": "5",
    "distance_unit": "in",
    "weight": "2",
    "mass_unit": "lb",
}

# Example CustomsItems object.
#  The complete reference for customs object is here: https://goshippo.com/docs/reference#customsitems
customs_item = {
    "description": "T-Shirt",
    "quantity": 2,
    "net_weight": "400",
    "mass_unit": "g",
    "value_amount": "20",
    "value_currency": "USD",
    "origin_country": "US",
    "tariff_number": "",
}

# Creating the CustomsDeclaration
# The details on creating the CustomsDeclaration is here: https://goshippo.com/docs/reference#customsdeclarations
customs_declaration = shippo.CustomsDeclaration.create(
    contents_type="MERCHANDISE",
    contents_explanation="T-Shirt purchase",
    non_delivery_option="RETURN",
    certify=True,
    certify_signer="Mr Hippo",
    items=[customs_item],
)

# Creating the shipment object. asynchronous=False indicates that the function will wait until all
# rates are generated before it returns.

# The reference for the shipment object is here: https://goshippo.com/docs/reference#shipments
# By default Shippo API operates on an async basis. You can read about our async flow here: https://goshippo.com/docs/async
shipment_international = shippo.Shipment.create(
    address_from=address_from,
    address_to=address_to_international,
    parcels=[parcel],
    customs_declaration=customs_declaration.object_id,
    asynchronous=False,
)

# Get the first rate in the rates results for demo purposes.
# The details on the returned object are here: https://goshippo.com/docs/reference#rates
rate_international = shipment_international.rates[0]

# Purchase the desired rate.
# The complete information about purchasing the label: https://goshippo.com/docs/reference#transaction-create
transaction_international = shippo.Transaction.create(rate=rate_international.object_id, asynchronous=False)

# print label_url and tracking_number
if transaction_international.status == "SUCCESS":
    print(f"Purchased label with tracking number {transaction_international.tracking_number}")
    print(f"The label can be downloaded at {transaction_international.label_url}")
else:
    print("Failed purchasing the label due to:")
    for message in transaction_international.messages:
        print(f"- {message['text']}")

# For more tutorials of address validation, tracking, returns, refunds, and other functionality, check out our
# complete documentation: https://goshippo.com/docs/

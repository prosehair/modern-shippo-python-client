"""
In this tutorial we have an order with a sender address,
recipient address and parcel information that we need to ship.

In addition to that we know that the customer expects the
shipment to arrive within 3 days. We want to purchase
the cheapest shipping label with a transit time <= 3 days.
"""

import shippo

# for demo purposes we set the max. transit time here
MAX_TRANSIT_TIME_DAYS = 3

# Replace <API-KEY> with your key
shippo.config.api_key = "<API-KEY>"

# Example address_from object dict
# The complete refence for the address object is available here: https://goshippo.com/docs/reference#addresses
address_from = {
    "name": "Mrs Hippo",
    "street1": "215 Clayton St.",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94117",
    "country": "US",
    "phone": "+1 555 341 9393",
}

# Example address_to object dict
# The complete refence for the address object is available here: https://goshippo.com/docs/reference#addresses

address_to = {
    "name": "Mr. Hippo",
    "street1": "1092 Indian Summer Ct",
    "city": "San Jose",
    "state": "CA",
    "zip": "95122",
    "country": "US",
    "phone": "+1 555 341 9393",
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

# Creating the shipment object. asynchronous=False indicates that the function will wait until all
# rates are generated before it returns.
# The reference for the shipment object is here: https://goshippo.com/docs/reference#shipments
# By default Shippo API operates on an async basis. You can read about our async flow here: https://goshippo.com/docs/async
shipment = shippo.Shipment.create(address_from=address_from, address_to=address_to, parcels=[parcel], asynchronous=False)

# Rates are stored in the `rates` array
# The details on the returned object are here: https://goshippo.com/docs/reference#rates
rates = shipment.rates

# filter rates by max. transit time, then select cheapest
eligible_rate = (rate for rate in rates if rate["estimated_days"] <= MAX_TRANSIT_TIME_DAYS)
rate = min(eligible_rate, key=lambda x: float(x["amount"]))
print(
    f"Picked service {rate['provider']} {rate['servicelevel']['name']} for {rate['currency']} {rate['amount']} with est."
    f" transit time of {rate['estimated_days']} days"
)

# Purchase the desired rate. asynchronous=False indicates that the function will wait until the
# carrier returns a shipping label before it returns
transaction = shippo.Transaction.create(rate=rate.object_id, asynchronous=False)

# print label_url and tracking_number
if transaction.status == "SUCCESS":
    print(f"Purchased label with tracking number {transaction.tracking_number}")
    print(f"The label can be downloaded at {transaction.label_url}")
else:
    print("Failed purchasing the label due to:")
    for message in transaction.messages:
        print(f"- {message['text']}")

# For more tutorals of address validation, tracking, returns, refunds, and other functionality, check out our
# complete documentation: https://goshippo.com/docs/

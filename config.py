# Klaviyo account
public_key = 'abc123'


# order example
# order_mapping: left = klaviyo key, right = item_mapping key
# must have $event_id, $email, time
# note, this wrapper makes a distinction between standard order properties and listed/summed properties that require merging events
# description is a reserved key; additional reserved keys in klaviyo docs
order_mapping = {
    'event':'PlacedOrder',
    'customer_properties':{
        '$email':'EMAIL',
    },
    'properties':{
        '$event_id':'ORDER_ID',
        'OrderType':'ORDER_TYPE',
    },
    'summed_properties':{
        '$value':'ITEM_PRICE'
    },
    'listed_properties':{
        'ItemNames':'ITEM_NAME',
        'CouponCodes':'COUPON_CODE'
    },
    'time':'UNIX_TIME'
}


# item example
# item_mapping: left = klaviyo key, right = corresponding column name
# item mapping must include, at a minimum: $value, $event_id, time, $email, and OrderID
item_mapping = {
    'event':'OrderedItem',
    'customer_properties':{
        '$email':'EMAIL',
    },
    'properties':{
        '$event_id':'ITEM_ID',
        '$value':'ITEM_PRICE',
        'OrderID':'ORDER_ID',
        'OrderType':'ORDER_TYPE',
        'CouponCode':'COUPON_CODE',
        'ItemName':'ITEM_NAME'
    },
    'time':'UNIX_TIME'
}


# profile property example
# edit this to conform to your data, or delete 
profile_mapping = {
    'properties': {
        '$email':'EMAIL',
        '$first_name':'FIRST_NAME',
        '$last_name':'LAST_NAME',
        '$zip':'ZIP',
        '$phone_number' : 'PHONE',
    }
}

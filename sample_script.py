from utils import *
import config

# filename = sys.argv[1]
filename = 'complete_ordered_items.csv'

# generate list of payloads from csv
items = csv_to_payloads(config.public_key, config.item_mapping, filename)
orders = csv_to_orders(config.public_key, config.order_mapping, filename, items)
profiles = csv_to_payloads(config.public_key, config.profile_mapping, filename)

# send all item/order events to klaviyo using all cores, and save responses
item_responses = parallelize(send_event_payload, items)
order_responses = parallelize(send_event_payload, orders)
profile_responses = parallelize(send_profile_payload, profiles)

# filter repsonses above for payloads that should be re-sent
failed_item_payloads = [response for response in item_responses if response != None]
failed_order_payloads = [response for response in order_responses if response != None]
failed_profile_payloads = [response for response in profile_responses if response != None]

# # print count of failures
print('# failed item payloads',len(failed_item_payloads))
print('# failed order payloads',len(failed_order_payloads))
print('# failed profile payloads',len(failed_profile_payloads))

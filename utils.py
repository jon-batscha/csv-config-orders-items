import json
import multiprocessing
import math
import time
import base64
import csv
import os
import sys
import copy
import requests
import datetime
import random


# Klaviyo
def send_event_payload(payload):
    '''
    input: payload of event object
    output: None (successfully sent) or unencoded payload (on failure)
    action: sends a complete event payload to metrics api
    '''

    set_event_id(payload)
    set_timestamp(payload)

    endpoint = 'https://a.klaviyo.com/api/track'

    encoded_payload = base64.b64encode(json.dumps(payload).encode('utf-8'))

    params = {'data': encoded_payload}

    while True:

        response = requests.get(endpoint, params=params)

        if response.status_code == 200:

            return None

        elif response.status_code == 429:

            time.sleep(10)

        else:

            return payload


def send_profile_payload(payload):
    '''
    input: payload of profile object
    output: None (successfully sent) or unencoded payload (on failure)
    action: sends a complete profile payload to identify api 
    '''

    endpoint = 'https://a.klaviyo.com/api/identify'

    encoded_payload = base64.b64encode(json.dumps(payload).encode('utf-8'))

    params = {'data': encoded_payload}

    while True:

        response = requests.get(endpoint, params=params)

        if response.status_code == 200:

            return None

        elif response.status_code == 429:

            time.sleep(10)

        else:

            return payload


def set_timestamp(payload):
    '''
    input: payload for event
    ouput: None
    action: sets event "time" according to logic laid out in docs
    '''

    if 'time' not in payload.keys():
        payload['time'] = '' #int(time.time())
    elif type(payload['time']) == str:
        if payload['time'].isnumeric():
            payload['time'] = int(payload['time'])
        else:
            payload['time'] = int(datetime.datetime.fromisoformat(payload['time']).timestamp())

    return None


def set_event_id(payload):
    '''
    input: payload for event
    ouput: None
    action: sets $event_id according to logic laid out in docs
    '''

    if '$event_id' not in payload['properties'].keys():

        payload['properties']['$event_id'] = str(abs(hash(str(payload))))

    elif not payload['properties']['$event_id'] or payload['properties']['$event_id'] == '':

            payload['properties']['$event_id'] = str(abs(hash(str(payload))))

    return None


def csv_to_payloads(public_key, mapping, filepath):
    '''
    input: config.public_key, config.mapping, filepath
    output: list of payloads
    NOTE: will not work for further nested objects, such as orders; for orders, use csv_to_orders(...)
    '''

    # get data and headers into list of lists
    with open(filepath,'r',encoding='utf-8-sig') as f:

        reader = csv.reader(f)

        data = list(reader)

    headers = data.pop(0)

    # name to col
    name_to_col = {}
    for i in range(len(headers)):

        name_to_col[headers[i]]=i

    # create list of json objs

    objs = []

    for row in data:

        obj = copy.deepcopy(mapping)
        keys = list(obj.keys())

        for key in keys:

            if key == 'event':

                continue

            elif type(obj[key]) == str:

                value = row[name_to_col[obj[key]]]

                if value != '':

                    obj[key] = value

                else:

                    del obj[key]

            elif type(obj[key]) == dict:

                subkeys = list(obj[key].keys())

                for subkey in subkeys:
                    
                    value = row[name_to_col[obj[key][subkey]]]

                    if value != '':

                        obj[key][subkey] = value

                    else:

                        del obj[key][subkey]

            else:

                print('ERROR: neither string nor dict')
                return False

        obj['token'] = public_key

        if 'event' in mapping.keys():
            obj['event'] = mapping['event']

        objs.append(copy.deepcopy(obj))

    # for payload in objs:

    #     set_timestamp(payload)
    #     set_event_id(payload)

    return objs


def csv_to_orders(public_key, mapping, filepath, ordered_items_list):
    '''
    input: config.public_key, config.mapping, filepath, ordered_items_list
    output: list of order payloads
    '''

    # get data and headers into list of lists
    with open(filepath,'r',encoding='utf-8-sig') as f:

        reader = csv.reader(f)

        data = list(reader)

    headers = data.pop(0)

    # name to col
    name_to_col = {}
    for i in range(len(headers)):

        name_to_col[headers[i]]=i

    #initialize order_if to order dict
    order_dict = dict()

    # create list of json objs
    objs = []

    for row in data:

        # get order_id; if new, pre_fill and add to dict; else, retrieve order
        order_id = row[name_to_col[mapping['properties']['$event_id']]]

        if order_id not in order_dict:

            order = {
                'event':mapping['event'],
                'token':public_key,
                'time':row[name_to_col[mapping['time']]],
                'customer_properties':{
                    '$email':row[name_to_col[mapping['customer_properties']['$email']]],
                },
                'properties':{},
                'summed_properties':{},
                'listed_properties':{}
            }

            for summed_prop in mapping['summed_properties']:

                order['summed_properties'][summed_prop] = 0

            for listed_prop in mapping['listed_properties']:

                order['listed_properties'][listed_prop] = []

            for key in mapping['properties']:

                order['properties'][key] = row[name_to_col[mapping['properties'][key]]]

            order_dict[order_id] = copy.deepcopy(order)
        
        order = order_dict[order_id]

        # sum properties
        for key in mapping['summed_properties']:

            value = row[name_to_col[mapping['summed_properties'][key]]]

            if value.isnumeric():

                if order['summed_properties'][key] == 0:
                    order['summed_properties'][key] = eval(value)
                else:

                    order['summed_properties'][key] += eval(value)

        # addlisted properties
        for key in mapping['listed_properties']:

            value = row[name_to_col[mapping['listed_properties'][key]]]

            if value != '' and value not in order['listed_properties'][key]:

                order['listed_properties'][key].append(value)

    # merge standard/listed/summed properties
    merge_keys = ['listed_properties','summed_properties']
    for order_id in order_dict:

        order = order_dict[order_id]


        for key in merge_keys:

            order['properties'].update(order[key])

            del order[key]


    # # add items to properties
    # for item in ordered_items_list:

    #     if 'Items' not in order_dict[item['properties']['OrderID']]['properties'].keys():

    #         order_dict[item['properties']['OrderID']]['properties']['Items'] = []

    #     order_dict[item['properties']['OrderID']]['properties']['Items'].append(item['properties'])

    payloads = list(order_dict.values())

    # for payload in payloads:

    #     set_timestamp(payload)
    #     set_event_id(payload)

    return payloads


# Threading
def parallelize(function,args):
    '''
    input: function, list of args
    output: list of outputs from function applied to each arg
    '''

    cores = multiprocessing.cpu_count()

    pool = multiprocessing.Pool(processes=cores)

    outputs = pool.map(function,args)

    return outputs










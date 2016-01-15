#!/usr/bin/env python

# Scrapes a whole city from Yelp.

import argparse, csv, collections, ConfigParser, time, json
from yelpapi import YelpAPI

parser = argparse.ArgumentParser()
parser.add_argument('--neighborhoods_file', default='data/sffind_neighborhoods.json')
parser.add_argument('--config_file', default='config.txt')
parser.add_argument('--output_file', default='yelp_results.json')
parser.add_argument('--limit', help='stop after N businesses, for testing', type=int)
args = parser.parse_args()

config = ConfigParser.ConfigParser()
config.read('config.txt')
yelp_api = YelpAPI(config.get('yelp', 'consumer_key'),
        config.get('yelp', 'consumer_secret'), config.get('yelp', 'token'),
        config.get('yelp', 'token_secret'))

# https://www.yelp.com/developers/documentation/v2/search_api
all_businesses = []
num_results_so_far = 0
while True:
    results = yelp_api.search_query(category_filter='coffee',
        location='San Francisco, CA', offset=num_results_so_far)
    print results['total']
    for business in results['businesses']:
        if business['is_closed']:
            print "Not including, permanently closed: %s" % business['name']
            continue
        try:
            all_businesses.append({'name': business['name'],
                'latitude': business['location']['coordinate']['latitude'],
                'longitude': business['location']['coordinate']['longitude'],
            })
        except:
            print "Error with this business:"
            print business
            continue

    num_results_so_far += len(results['businesses'])
    if num_results_so_far >= results['total'] or\
            (args.limit and num_results_so_far >= args.limit):
        break
    time.sleep(3)

json.dump(all_businesses, open(args.output_file, 'w'), indent=2)


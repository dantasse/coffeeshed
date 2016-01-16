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
# bounds=sw_latitude,sw_longitude|ne_latitude,ne_longitude
# bounds = '37.70,-122.5|37.76,-122.35' # lower half of SF
# bounds = '37.76,-122.5|37.82,-122.35' # upper half of SF
bounds = '37.70,-122.55|37.82,-122.35' # all SF, rough handmade query.
while True:
    try:
        # results = yelp_api.search_query(category_filter='coffee',
        #     location='San Francisco, CA', offset=num_results_so_far)
        results = yelp_api.search_query(category_filter='coffee',
            bounds=bounds, offset=num_results_so_far)
    except Exception as e:
        print "Error sending request, writing file and quitting."
        print e
        break

    print "This many so far: %d, this many total: %d" % (num_results_so_far, results['total'])
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
    time.sleep(2)

json.dump(all_businesses, open(args.output_file, 'w'), indent=2)


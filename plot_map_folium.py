#!/usr/bin/env python

# Uses the Folium library to plot a simple map.

import folium, ujson, argparse

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--coffeeshops_file', default='yelp_results_sf_bbox.json')
    parser.add_argument('--map_output_file', default='coffeemap.html')
    args = parser.parse_args()

    map_1 = folium.Map(location=[37.783333, -122.416667], zoom_start=13)
    for shop in ujson.load(open(args.coffeeshops_file)):
        map_1.simple_marker([shop['latitude'], shop['longitude']], popup=shop['name'])
    map_1.create_map(path=args.map_output_file)


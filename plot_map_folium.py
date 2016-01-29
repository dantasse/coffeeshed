#!/usr/bin/env python

# Uses the Folium library to plot a simple map.

import folium, ujson, argparse
from scipy.spatial import Voronoi

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--coffeeshops_file', default='yelp_results_sf_bbox.json')
    parser.add_argument('--map_output_file', default='coffeemap.html')
    args = parser.parse_args()

    points = []
    map = folium.Map(location=[37.783333, -122.416667], zoom_start=13)
    for shop in ujson.load(open(args.coffeeshops_file)):
        lat = shop['latitude']
        lon = shop['longitude']
        if lat < 37.71 or lat > 37.82 or lon < -122.522 or lon > -122.35:
            continue # rough bounds. hacky, fine. works b/c SF is squarish.
        map.simple_marker([lat, lon], popup=shop['name'])
        points.append([lat, lon])

    vor = Voronoi(points)
    for vert1, vert2 in vor.ridge_vertices:
        # each one is a pair [vert1, vert2]
        point1 = vor.vertices[vert1]
        if vert1 < 0 or vert2 < 0:
            continue
        point2 = vor.vertices[vert2]
        
        map.line(locations=[point1, point2])    
    map.create_map(path=args.map_output_file)


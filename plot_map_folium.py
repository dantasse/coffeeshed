#!/usr/bin/env python

# Uses the Folium library to plot a simple map.

import folium, ujson, argparse, numpy as np, shapely
from shapely.geometry import LineString, LinearRing, Polygon
from scipy.spatial import Voronoi

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--coffeeshops_file', default='yelp_results_sf_bbox.json')
    parser.add_argument('--map_output_file', default='coffeemap.html')
    args = parser.parse_args()

    points = []
    map = folium.Map(location=[37.783333, -122.416667], tiles='Stamen Toner', zoom_start=13)
    for shop in ujson.load(open(args.coffeeshops_file)):
        lat = shop['latitude']
        lon = shop['longitude']
        # TODO factor out these constants
        if lat < 37.71 or lat > 37.82 or lon < -122.52 or lon > -122.35:
            continue # rough bounds. hacky, fine. works b/c SF is squarish.
        map.simple_marker([lat, lon], popup=shop['name'])
        points.append([lat, lon])

    bounds1 = np.array([37.71, -122.52])
    bounds2 = np.array([37.82, -122.52])
    bounds3 = np.array([37.82, -122.35])
    bounds4 = np.array([37.71, -122.35])
    # TODO make this a polygon around SF
    bounds = Polygon([bounds1, bounds2, bounds3, bounds4])
    vor = Voronoi(points)
    # ridge_vertices is the "voronoi lines".
    for vert1, vert2 in vor.ridge_vertices:
        # each one is a pair [vert1, vert2]
        if vert1 < 0 or vert2 < 0:
            continue
        point1 = np.array(vor.vertices[vert1])
        point2 = np.array(vor.vertices[vert2])
        line1 = LineString([point1, point2])
        if line1.crosses(bounds):
            print line1.intersection(bounds).coords[:]
            # TODO figure out which half is within the bounding box, and only draw that line.
            # map.line(locations=[point1, line1.intersection(bounds).coords[:][0]], line_color="red")    
            map.line(locations=[point1, point2], line_color="red")    
        elif not line1.within(bounds):
            # map.line(locations=[point1, point2], line_color="green")    
            continue # don't draw this, it's outside SF
        else:
            map.line(locations=[point1, point2])

    map.create_map(path=args.map_output_file)


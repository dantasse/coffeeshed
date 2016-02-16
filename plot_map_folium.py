#!/usr/bin/env python

# Uses the Folium library to plot a simple map.

import folium, ujson, argparse, numpy as np, shapely, cgi
from shapely.geometry import LineString, LinearRing, Polygon, Point
from scipy.spatial import Voronoi
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def draw_print_map(vor):
    """|vor| is a scipy.spatial.qhull.Voronoi object. """
    
    print vor

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--coffeeshops_file', default='yelp_results_sf_bbox.json')
    parser.add_argument('--map_output_file', default='coffeemap.html')
    args = parser.parse_args()

    points = [[39.78, -122.41], [35.78, -122.41], [37.78, -120.41], [37.78, -124.41]]
    # Start with dummy points so Voronoi lines don't go off to infinity.

    map = folium.Map(location=[37.783333, -122.416667], tiles='Stamen Toner', zoom_start=12)
    for shop in ujson.load(open(args.coffeeshops_file)):
        lat = shop['latitude']
        lon = shop['longitude']
        # TODO factor out these constants
        if lat < 37.71 or lat > 37.82 or lon < -122.52 or lon > -122.35:
            continue # rough bounds. hacky, fine. works b/c SF is squarish.
        # map.simple_marker([lat, lon], popup=shop['name'])
        folium.Marker(
            [lat, lon],
            icon=folium.features.DivIcon(
                icon_size=(150,36),
                icon_anchor=(0,0),
                html="<div>" + cgi.escape(shop['name'].replace("'", "\\'")) + "</div>",
            )
        ).add_to(map)
        points.append([lat, lon])

    bounds1 = np.array([37.71, -122.52])
    bounds2 = np.array([37.82, -122.52])
    bounds3 = np.array([37.82, -122.35])
    bounds4 = np.array([37.71, -122.35])
    bounds = Polygon([bounds1, bounds2, bounds3, bounds4])
    map.add_children(folium.PolyLine(locations=bounds.exterior.coords))
    vor = Voronoi(points)

    draw_print_map(vor)
    geo_axes = plt.axes(projection=ccrs.PlateCarree())
    # geo_axes.coastlines()
    geo_axes.stock_img()
    geo_axes.gridlines()
    geometries = [] # Stuff to go on the print map.
    geo_axes.set_extent([-120, -115, 30, 35], ccrs.PlateCarree())
    geo_axes.plot(-117.1625, 32.715, 'bo', markersize=7, transform=ccrs.Geodetic())
    geo_axes.plot(-118.1625, 33.715, 'bo', markersize=7, transform=ccrs.Geodetic())
    geo_axes.text(-117, 33, 'San Diego', transform=ccrs.Geodetic())
    geo_axes.set_xmargin(0.05)
    geo_axes.set_ymargin(0.10) 

    # ridge_vertices is the "voronoi lines".
    for vert1, vert2 in vor.ridge_vertices:
        # each one is a pair [vert1, vert2]
        if vert1 < 0 or vert2 < 0:
            continue
        point1 = np.array(vor.vertices[vert1])
        point2 = np.array(vor.vertices[vert2])
        line1 = LineString([point1, point2])
        if line1.crosses(bounds):
            line_within = line1.intersection(bounds)
            map.add_children(folium.PolyLine(locations=line_within.coords))
            # |bounds| is a polygon so the intersection is the part that is
            # within the polygon.
            geometries.append(line_within)
        elif not line1.within(bounds):
            continue # don't draw this, it's outside SF
        else:
            map.add_children(folium.PolyLine(locations=[point1, point2]))
            geometries.append(line1)

    map.save(args.map_output_file)

    geo_axes.add_geometries(geometries, ccrs.PlateCarree())
    plt.show()

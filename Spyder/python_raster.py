import rasterio as rio
from matplotlib import pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib
import geopandas as gpd
import os

from shapely.geometry import box
from shapely.geometry import Polygon
import pyproj
from shapely.ops import transform

# examples = 'ExamplesMSsmallCop'
# examples = 'ExamplesMSbigCop'
examples = 'Example'

gross_agg = gpd.read_file('data/gross/agg_results.geojson')
klein_fertig = gpd.read_file('D:/Bachelorarbeit/Project/QGIS/reference/agg_fertig.shp')
klein_agg = gpd.read_file('data/klein/agg_results.geojson')
cop_buildings = gpd.read_file('data/cop/cop_clipped_footprints.shp')
# cop_buildings = gpd.read_file('data/cop/ems.shp')
cop_buildings_moved = gpd.read_file('data/cop/cop_footprints_moved.shp')

cop = cop_buildings
agg = gross_agg

gross = True


def get_number(string):
    num = ""
    for c in string:
        if c.isdigit():
            num = num + c

    return int(num)


names = os.listdir(f'outputs/rasters/{examples}')

lims = (205, 195)

if names[0][3:8] == 'small':
    agg = klein_agg
    cop = cop_buildings_moved
    lims = (1484, 1474)
    gross = False

idx = [get_number(string) for string in names]
infos = [[agg.loc[agg['idx'] == i], klein_fertig.loc[klein_fertig['idx'] == i]] for i in idx]

if gross:
    infos = [[agg.loc[agg['idx'] == i], " "] for i in idx]



examples4 = [None] * len(names)
for i, name in enumerate(names):
    examples4[i] = rio.open(f"outputs/rasters/{examples}/{name}")


def make_rgb(raster):
    red = raster.read(1)
    green = raster.read(2)
    blue = raster.read(3)

    def normalize(array):
        """Normalizes numpy arrays into scale 0.0 - 1.0"""

        array_min, array_max = array.min(), array.max()
        return ((array - array_min)/(array_max - array_min))

    red = normalize(red)
    green = normalize(green)
    blue = normalize(blue)

    rgb = np.dstack((red, green, blue))

    return rgb


crs_old = examples4[0].crs

wgs84 = pyproj.CRS('EPSG:4326')
project = pyproj.Transformer.from_crs(crs_old, wgs84, always_xy=True).transform
#utm_point = transform(project, wgs84_pt)


def trans(clip_df, bound_polygon):
    bounds = bound_polygon.bounds
    xmin = bounds[0]
    xmax = bounds[2]
    ymin = bounds[1]
    ymax = bounds[3]

    xx = (xmax-xmin)
    yy = (ymax-ymin)

    if len(clip_df) == 0:
        return

    # clip_df = clip_df.dissolve()
    shapely_poly = list(clip_df.geometry)

    all_polys = []
    for poly in shapely_poly:
        x, y = poly.exterior.xy
        x, y = list(x), list(y)

        x = [(val-xmin)*lims[0]/xx for val in x]
        y = [lims[1]-(val-ymin)*lims[1]/yy for val in y]

        all_polys.append(Polygon(zip(x, y)))
    return all_polys


bounds = [transform(project, box(*ex.bounds)) for ex in examples4]
copernicus_clips = [gpd.clip(cop, box) for box in bounds]

new_polys = [trans(clip, bound)
             for clip, bound in zip(copernicus_clips, bounds)]

rgbs = [make_rgb(raster) for raster in examples4]

# rgbs[1], rgbs[3] = rgbs[3], rgbs[1]
# infos[1], infos[3] = infos[3], infos[1]

# rgbs[0], rgbs[1] = rgbs[1], rgbs[0]
# infos[0], infos[1] = infos[1], infos[0]
# new_polys[0], new_polys[1] = new_polys[1], new_polys[0]

# rgbs[0], rgbs[1], rgbs[3] = rgbs[1], rgbs[3], rgbs[0]
# infos[0], infos[1], infos[3] = infos[1], infos[3], infos[0]
# new_polys[0], new_polys[1], new_polys[3] = new_polys[1], new_polys[3], new_polys[0]


rgbs[0][rgbs[0] == 0] = 1
rgbs[1][rgbs[1] == 0] = 1

#rgbs = rgbs[:2]
s = "MapSwipe:\nIdx: {} \nYes: {}\nMaybe: {}\nNo: {}"

# s += "\nBad Imagery: {}"
s += "\nReference: {}"


if gross:
    s = "MapSwipe:\nIdx: {} \nYes: {}\nMaybe: {}\nNo: {}{}"

if len(rgbs) == 4:
    fig = plt.figure(figsize=(16, 16))
    ax = [fig.add_subplot(2, 2, i+1) for i in range(4)]

    gs1 = gridspec.GridSpec(2, 2)
    gs1.update(wspace=0.01, hspace=0.02)  # set the spacing between axes.

    letters = ['a', 'b', 'c', 'd']
    
    
    for i in range(4):
        info = infos[i]
        
        if gross:
            final_lab = ""
            
        else:
            final_lab = str(info[1]['Final Labe'].values[0])[0]
            
        string = s.format(str(int(info[0]['idx'].values[0])), str(info[0]['1_count'].values[0])[
                          0], str(info[0]['2_count'].values[0])[0], str(info[0]['0_count'].values[0])[0],
                            final_lab)

        a = plt.subplot(gs1[i])

        plt.xticks([])
        plt.yticks([])
        a.set_aspect('equal')
        a.imshow(rgbs[i])

        if new_polys[i] is not None:
            cols = {'Destroyed': 'red', 'Damaged': 'red',
                    'Possibly damaged': 'yellow'}
            already = []

            legends = []
            names = []

            for j, poly in enumerate(new_polys[i]):
                status = list(copernicus_clips[i].damage_gra)[j]

                x, y = poly.exterior.xy
                ext = plt.plot(x, y, linewidth=5, color=cols[status])
                if status == 'Damaged' or status == 'Destroyed':
                    status = 'Damaged/Destroyed'

                if status not in already:
                    already.append(status)

                    legends.append(ext[0])
                    names.append(f'CEMS Buildings "{status}"')

        plt.text(0.79, 0.05, string,
                 fontsize=12,
                 transform=a.transAxes,
                 bbox={'facecolor': 'white',
                       'pad': 10})

        # plt.text(0.2, 0.5, letters[i], fontsize=16, color='black')
        if new_polys[i] is not None:
            plt.legend(legends, names, loc='best', fontsize=12)


if len(rgbs) == 2:
    
    fig = plt.figure(figsize=(16, 16))
    ax = [fig.add_subplot(2, 2, i+1) for i in range(2)]

    gs1 = gridspec.GridSpec(2, 2)
    gs1.update(wspace=0.05, hspace=0.0)  # set the spacing between axes.

    for i in range(2):
        info = infos[i]
        string = s.format(str(int(info[0]['idx'].values[0])), str(info[0]['1_count'].values[0])[
                          0], str(info[0]['2_count'].values[0])[0], str(info[0]['0_count'].values[0])[0],
                            str(info[0]['3_count'].values[0])[0],
                            str(info[1]['Final Labe'].values[0])[0])
        
        
        
        a = plt.subplot(gs1[i])

        # a.axis('off')
        plt.xticks([])
        plt.yticks([])
        a.set_aspect('equal')
        
        a.imshow(rgbs[i])
        # a.imshow(masked_array, interpolation='nearest', cmap=cmap)

        plt.text(0.28, 0.71, string,
                 fontsize=14,
                 verticalalignment='bottom',
                 horizontalalignment='right',
                 transform=a.transAxes,
                 bbox={'facecolor': 'white',
                       'pad': 10})


if len(rgbs) == 1:
    fig, ax = plt.subplots(1, figsize=(6, 6))
    

    info = agg.loc[agg['idx'] == idx[0]]
    string = s.format(str(int(info['idx'].values[0])), str(info['1_count'].values[0])
                      , str(info['2_count'].values[0]), str(info['0_count'].values[0]), "")

    # a.axis('off')
    plt.xticks([])
    plt.yticks([])
    ax.set_aspect('equal')
    ax.imshow(rgbs[0])

    # plt.text(0.70, 0.05, string,
    #           fontsize=14,
    #           verticalalignment='bottom',
    #           horizontalalignment='left',
    #           transform=ax.transAxes,
    #           bbox={'facecolor': 'white',
    #                 'pad': 10})
  
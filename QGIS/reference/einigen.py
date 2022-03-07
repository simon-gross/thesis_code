# -*- coding: utf-8 -*-
"""
Created on Fri Feb 18 16:12:01 2022

@author: Simsi_Arbeit
"""

import geopandas as gpd
import pandas as pd

agg = gpd.read_file("D:/Bachelorarbeit/Project/QGIS/reference/agg_results.geojson")

fertig = gpd.read_file("D:/Bachelorarbeit/Project/QGIS/reference/fertig.geojson")

agg = agg.drop(columns=['0_share', '1_share', '2_share', '3_share', \
                        'quadkey', 'Unnamed: 0', 'taskX', 'taskY', 'url', 'urlB'])


def fun(row):
    if row['3_count'] > 0:
        row['3_count'] = 0
        row['0_count'] += 1
        row['agreement'] = 1
    
    return row
        
agg = agg.apply(fun, axis=1)

kurz = agg[agg['agreement'] < 1]

kurz = kurz.task_id.sort_values().values
fertig2 = fertig.task_id.sort_values().values

print(all(kurz==fertig2))

def fun2(row):
    if row['agreement'] < 1:
        task_id = row['task_id']
        
        fin_label = fertig.loc[fertig['task_id'] == task_id]['Final Label'].iloc[0]
        return fin_label
    
    else:
        if row['0_count'] == 2:
            return 0
        if row['1_count'] == 2:
            return 1
        else:
            raise ValueError('SCHEISSE!')
        

agg['Final Label'] = agg.apply(fun2, axis=1)
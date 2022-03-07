# -*- coding: utf-8 -*-
"""
Created on Fri Feb 18 15:46:23 2022

@author: Simsi_Arbeit
"""

import pandas as pd

a = pd.read_csv("D:/Bachelorarbeit/Project/QGIS/reference/results_-MupztNOQu1l60QmSvY6.csv")

mask = a.user_id!="X0zTSyvY0khDfRwc99aQfIjTEPK2"

a = a[mask]

benni = a[a['user_id'] == 'osm:12485'].sort_values(by='task_id')

simon = a[a['user_id'] == '4IZxPS6gOWaMGjtdn3I8ETlaXFF2'].sort_values(by='task_id')

mask_einigkeit = [True if b == s else False for b, s in zip(benni.result, simon.result)]

mask_uneinig = [not val for val in mask_einigkeit]

uneingig = simon.index[mask_uneinig]

uneingig.to_csv('D:/Bachelorarbeit/Project/QGIS/reference/uneinig.csv')
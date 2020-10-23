import os
import pickle
import pandas as pd
import numpy as np
import math
import csv

def PolygonArea(corners):
    n = len(corners)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
    area = abs(area) / 2.0
    return area


def CentralityRating(width, height, area, corners):
    h_to_w = float(height/width)
    w = float(math.sqrt(area/h_to_w))
    h = float(area/w)
    x_1, x_2, y_1, y_2  = float(width/2 - w/2), float(width/2 + w/2), float(height/2 - h/2), float(height/2 + h/2)
    center = np.array([[x_1, y_1], [x_2, y_1], [x_2, y_2], [x_1, y_2]])
    diff = abs(center - corners)
    xmax, ymax = diff.max(axis=0)
    xmax = xmax/width
    ymax = ymax/height
    dislocation = math.sqrt(xmax*xmax + ymax*ymax)
    return dislocation

def save_obj(filename, dictionary):
    with open(filename, 'wb') as f:
        pickle.dump(dictionary, f, pickle.HIGHEST_PROTOCOL)
    # with open(filename + '_num_processed.txt', 'w') as l:
    #     l.write(str(num_processed))

def load_obj(filename):
    load = {}
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            load = pickle.load(f)
        # with open(filename + '_num_processed.txt', 'rb') as l:
        #     num_processed = int(l.read())
    return load

def add_to_map(dict,key, item):
    if key in  dict.keys():
        dict[key].append(item)
    else:
        dict[key] = [item]

def load_from_csv(csv_path):
    with open(csv_path) as csvfile:
        buffer = csv.reader(csvfile)#, delimiter=' ', quotechar='|')
        return [x[0].replace(u'\ufeff', '') for x in buffer]
    # df = pd.read_csv(csv_path)
    # print(df)
    #

def num_unique_logos(polys):
    unique_logos = []
    for poly in polys:
        unique_logos.append(poly['classes'][0]['class'])
    return len(set(unique_logos))

def convert_to_np(indices):
    return np.array([[indices[0]['x'], indices[0]['y']], [indices[1]['x'], indices[1]['y']], [indices[2]['x'], indices[2]['y']], [indices[3]['x'], indices[3]['y']]])

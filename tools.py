import os
import pickle
import pandas as pd
import numpy as np
import math
import csv


##############################################################
# PolygonArea(double, double)
# This function calculates area of a given rectangular ploygon, since all polygons
# that contain logos are rectangular.
#
# inputs: width, height
# returns: area
def PolygonArea(width, height):
    return width * height


##############################################################
# CentralityRating(double, double, double, np.array())
# This function calculates a rating that determines how far off-center a logo
# is located. The rating is based on diagonal dislocation.
#
# inputs: width of the entire image, height of the entire image, area of the
# logo, and corners that make up the rectnagular polygon of the logo
# returns: double that represents the rating
def CentralityRating(width, height, l_width, l_height, corners):
    x_1, x_2, y_1, y_2  = float(width/2 - l_width/2), float(width/2 + l_width/2), float(height/2 - l_height/2), float(height/2 + l_height/2)
    centers = np.array([[x_1, y_1], [x_2, y_1], [x_2, y_2], [x_1, y_2]])
    diff = abs(centers - corners)
    xmax, ymax = diff.max(axis=0)
    xmax = xmax/width
    ymax = ymax/height
    dislocation = math.sqrt(xmax*xmax + ymax*ymax)
    return 1- dislocation


##############################################################
# save_obj(string, dict)
# This function saves a given dictionary into the given filename.
#
# inputs: filename is the path to the file where the dict will be saved,
# dictionary is the dict that will be saved there
# returns: None
def save_obj(filename, dictionary):
    with open(filename, 'wb') as f:
        pickle.dump(dictionary, f, pickle.HIGHEST_PROTOCOL)


##############################################################
# save_obj(string, dict)
# This function retreives a saved dictionary from a given filename.
#
# inputs: filename is the path to the file where the dict will be saved
# returns: the dict that was saved there
def load_obj(filename):
    load = {}
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            load = pickle.load(f)
    return load


##############################################################
# add_to_map(dict, string, [])
# This function inserts a new key value pair into the provided dictionary
# or appends the value to the list associated with the key in the dictionary.
#
# inputs: dict, key, item
# returns: None
def add_to_map(dict,key, item):
    if key in  dict.keys():
        dict[key].append(item)
    else:
        dict[key] = [item]

##############################################################
# load_from_csv(string)
# This function loads data from csv file and returns a list with all the image
# urls in the file.
#
# inputs: csv_path
# returns: list of image urls
def load_from_csv(csv_path):
    with open(csv_path) as csvfile:
        buffer = csv.reader(csvfile)
        return [x[0].replace(u'\ufeff', '') for x in buffer]


##############################################################
# num_unique_logos(JSON)
# This function returns the number of unique logos in an image given a json
# response from the API
#
# inputs: polys is the json object that contains all the logos
# returns: number of unique logos in the ploys object
def num_unique_logos(polys):
    unique_logos = []
    for poly in polys:
        unique_logos.append(poly['classes'][0]['class'])
    return len(set(unique_logos))


##############################################################
# get_width_and_height([[double, double]])
# This function calculates the width and height of a rectangular polygon
# given its vertices
#
# inputs: vertices is a list of 4 x,y coordinate pairs that create the polygon
# returns: width, height
def get_width_and_height(vertices):
    return (vertices[1]['x'] - vertices[0]['x']), (vertices[2]['y']- vertices[1]['y'])

##############################################################
# convert_to_np([[double, double]])
# This function converts a list of vertices from a 2D array into a 2D numpy
# array.
#
# inputs: vertices is a list of 4 x,y coordinate pairs
# returns: numpy array of the vertices
def convert_to_np(vertices):
    return np.array([[vertices[0]['x'], vertices[0]['y']], [vertices[1]['x'], vertices[1]['y']], [vertices[2]['x'], vertices[2]['y']], [vertices[3]['x'], vertices[3]['y']]])

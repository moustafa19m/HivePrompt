# importing the requests library
import requests
import statistics
import numpy as np
import json
from collections import defaultdict
import os
import tools
import config as cfg
import matplotlib.pyplot as plt


class Analyzer():
    def __init__(self):
        self.data = tools.load_from_csv(cfg.CSV_PATH)
        self.all_json = tools.load_obj(cfg.SAVING_FILE)
        self.mapping = {}
        self.stats = defaultdict(tuple)

    def collect_data(self, process_new=None):
        if process_new == None:
            process_new = len(self.data)
        for key in self.all_json.keys():
            self.process(self.all_json[key])
        start = len(self.all_json)
        end_range = process_new + len(self.all_json)
        if end_range > len(self.data):
            end_range = len(self.data)
        for i in range(start, end_range):
            r = self.process_post_request(self.data[i])
            self.all_json[self.data[i]] = r
            self.process(r)
        tools.save_obj(cfg.SAVING_FILE, self.all_json)

    def process_post_request(self, dp):
        req = {'Token': cfg.API_KEY,
                'image_url':dp}
        # sending post request and saving response as response object
        return requests.post(url = cfg.API_ENDPOINT, headers=cfg.HEADER, data=req).json()

    def process(self, r):
        # extracting response
        polys = r['status'][0]['response']['output'][0]['bounding_poly']
        width = r['status'][0]['response']['input']['media']['width']
        height = r['status'][0]['response']['input']['media']['height']
        num_logos = tools.num_unique_logos(polys)
        for poly in polys:
            logo = poly['classes'][0]['class']
            calrity = poly['meta']['clarity']
            corners = tools.convert_to_np(poly['vertices'])
            area = tools.PolygonArea(corners)
            cRating = tools.CentralityRating(width, height, area, corners)
            tools.add_to_map(self.mapping, logo, [calrity, area, cRating, num_logos])

    def get_recommended(self):

        for logo in self.mapping.keys():
            freq = len(self.mapping[logo])
            logo_stats = np.array(self.mapping[logo])
            clarity = logo_stats[:,0]
            area = logo_stats[:,1]
            cRating = logo_stats[:,2]
            numPolys = logo_stats[:,3]
            clarity_mean = statistics.mean(clarity)
            clarity_std = statistics.pstdev(clarity)
            area_mean = statistics.mean(area)
            area_std = statistics.pstdev(area)
            cRating_mean = statistics.mean(cRating)
            cRating_std = statistics.pstdev(cRating)
            numPolys_mean = statistics.mean(numPolys)
            self.stats[logo] = (freq, clarity_mean, clarity_std, area_mean, area_std, cRating_mean, cRating_std, numPolys_mean)

        return sorted(self.stats, key=lambda x: (-1*self.stats[x][0], -1*self.stats[x][5], -1*self.stats[x][3], -1*self.stats[x][1], -1*self.stats[x][6], -1*self.stats[x][7],  -1*self.stats[x][2], -1*self.stats[x][4]))

    def plot_for_feature(self, feature="all"):
        feature_to_ind = {
            "frequency" : 0,
            "clarity" : 1,
            "area": 3,
            "cRating" : 5,
            "numPolys" : 7
        }
        if feature == "all":
            for f in feature_to_ind.keys():
                plt.figure()
                self.create_plot(f, feature_to_ind[f])
        else:
            if feature in feature_to_ind.keys():
                self.create_plot(feature, feature_to_ind[feature])
        plt.show()

    def create_plot(self, feature, feature_ind):
        labels = np.array(list(self.stats.keys())[:10])
        values = None
        if feature_ind == 0 or feature_ind == 7:
            values = [self.stats[x][feature_ind] for x in labels]
            plt.bar(labels, values, width=0.2, color='g', align='center')
        else:
            values = [self.stats[x][feature_ind] for x in labels]
            plt.bar(labels, values, width=0.2, color='g', align='center')
            values = [self.stats[x][feature_ind+1] for x in labels]
            plt.bar(labels, values, width=0.2, color='r', align='center')
        plt.xlabel('Logos', fontweight='bold', color = 'orange', fontsize='17', horizontalalignment='center')
        plt.ylabel(feature, fontweight='bold', color = 'orange', fontsize='17', horizontalalignment='center')




if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.collect_data(2000)
    print(analyzer.get_recommended())
    # for param in ["frequency", "clarity", "area", "cRating", "numPolys"]:
    analyzer.plot_for_feature()
    with open('output/data.json', 'w') as outfile:
        for k in analyzer.all_json:
            json.dump(analyzer.all_json[k], outfile)

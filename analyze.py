# importing the requests library
import requests
import statistics
import numpy as np
import json
from collections import defaultdict
import os
import tools
import config as cfg


class Analyzer():
    def __init__(self):
        self.data = tools.load_from_csv(cfg.CSV_PATH)
        self.all_json = tools.load_obj(cfg.SAVING_FILE)
        self.mapping = {}

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
        stats = defaultdict(tuple)
        for logo in self.mapping.keys():
            freq = len(self.mapping[logo])
            logo_stats = np.array(self.mapping[logo])
            # print(logo_stats)
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
            stats[logo] = (freq, clarity_mean, clarity_std, area_mean, area_std, cRating_mean, cRating_std, numPolys_mean)

        return sorted(stats, key=lambda x: (-1*stats[x][0], -1*stats[x][5], -1*stats[x][3], -1*stats[x][1], -1*stats[x][6], -1*stats[x][7],  -1*stats[x][2], -1*stats[x][4]))


if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.collect_data(2000)
    with open('output/data.json', 'w') as outfile:
        for k in analyzer.all_json:
            json.dump(analyzer.all_json[k], outfile)

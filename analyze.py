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
        self.max_freq = 0
        self.max_area = 0
        self.max_shared_logos = 0
        plt.rc('font', size=8)


    ##############################################################
    # collect_data(int)
    # This method collects data analytics for each image.
    # It first loads the saved json_responses from previous calls
    # and fetches process_new number of new availble images in the
    # csv file. If there are no more data to fetch, it just loads
    # the saved responses processes it. The idea is to decrease the
    # number of calls to the API as much as possible until all collect_data
    # points has been collected.
    #
    # inputs: process_new is the number of new images to fetch from API
    # returns: None
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
        self.set_max_freq()
        tools.save_obj(cfg.SAVING_FILE, self.all_json)



    ##############################################################
    # process_post_request(string)
    # This method makes a post request to the API with a given image url
    # and returns the json object of the response
    #
    # inputs: url is the url of the image to analyze
    # returns: Json Object
    def process_post_request(self, url):
        req = {'Token': cfg.API_KEY,
                'image_url':url}
        # sending post request and saving response as response object
        return requests.post(url = cfg.API_ENDPOINT, headers=cfg.HEADER, data=req).json()



    ##############################################################
    # process(JSON)
    # This method populates the mapping dictionary with data from the
    # response from the API.
    # mapping: logo => [[data 1], [data 2] . . .]
    # Each data item is a list that contains the following information
    # about any given instance of the logo:
    # [clarity, area, cRating, num_logos]
    # cRating is a rating that determines how far the logo is from the center
    # of the image, and num_logos is the number of unique logos that share the
    # screen with the logo.
    #
    # inputs: r is response JSON object
    # returns: None
    def process(self, r):
        # extracting response
        polys = r['status'][0]['response']['output'][0]['bounding_poly']
        width = r['status'][0]['response']['input']['media']['width']
        height = r['status'][0]['response']['input']['media']['height']
        num_logos = tools.num_unique_logos(polys) - 1
        for poly in polys:
            logo = poly['classes'][0]['class']
            calrity = poly['meta']['clarity']
            w, h = tools.get_width_and_height(poly['vertices'])
            area = tools.PolygonArea(w, h)
            corners = tools.convert_to_np(poly['vertices'])
            cRating = tools.CentralityRating(width, height, w, h, corners)
            tools.add_to_map(self.mapping, logo, [calrity, area, cRating, num_logos])
            self.set_maxes(area, num_logos)



    ##############################################################
    # calculate_stats()
    # This method calculates stats per logo by parsing the mapping
    # dictionary and extracting the required fields. These stats will
    # later be used to determine the best logo location.
    # The stats include: the frequency of appearance of the logo, the average
    # clarity of the logo, the average cRating of the logo, the average number
    # of logos that share the screen with the logo, the average area occupied
    # by the logo, and the standarad deviations for these averages as well.
    #
    # inputs: None
    # returns: None
    def calculate_stats(self):
        for logo in self.mapping.keys():
            freq = float(len(self.mapping[logo])/self.max_freq)
            logo_stats = np.array(self.mapping[logo])
            clarity = logo_stats[:,0]
            area = logo_stats[:,1]/float(self.max_area)
            cRating = logo_stats[:,2]
            num_shared_logos = logo_stats[:,3]/float(self.max_shared_logos)
            clarity_mean = statistics.mean(clarity)
            clarity_std = statistics.pstdev(clarity)
            area_mean = statistics.mean(area)
            area_std = statistics.pstdev(area)
            cRating_mean = statistics.mean(cRating)
            cRating_std = statistics.pstdev(cRating)
            num_shared_logos_mean = statistics.mean(num_shared_logos)
            self.stats[logo] = (freq, clarity_mean, clarity_std, area_mean, area_std, cRating_mean, cRating_std, num_shared_logos_mean)


    ##############################################################
    # plot_for_feature(string)
    # A visualization tool for the top 10 logos based on a specified feature.
    # Features include frequency, clarity, area, cRating, and sharedLogos.
    # It is also possible to create plots of all features by pasing no argument.
    # Note that the method doesn't show the graph, and plt.show() should be
    # called.
    #
    # inputs: feature is the name of the parameter that will be plotted
    # returns: None
    def plot_for_feature(self, feature="all"):
        feature_to_ind = {
            "frequency" : 0,
            "clarity" : 1,
            "area": 3,
            "cRating" : 5,
            "sharedLogos" : 7
        }
        if feature == "all":
            for f in feature_to_ind.keys():
                plt.figure()
                self.create_feature_plot(f, feature_to_ind[f])
        else:
            if feature in feature_to_ind.keys():
                self.create_feature_plot(feature, feature_to_ind[feature])

    ##############################################################
    # create_feature_plot(string, int)
    # A helper method for plot_for_feature().
    #
    # inputs: feature is the name of the parameter that will be plotted
    #         feature_ind is the index of that feeature in self.stats
    # returns: None
    def create_feature_plot(self, feature, feature_ind):
        labels = np.array(list(self.stats.keys())[:10])
        values = None
        if feature_ind == 0 or feature_ind == 7:
            values = [self.stats[x][feature_ind] for x in labels]
            plt.bar(labels, values, width=0.2, color=(0, 1, 0, 1), align='center')
        else:
            values = [self.stats[x][feature_ind] for x in labels]
            plt.bar(labels, values, width=0.2, color=(0, 1, 0, 0.5), align='center')
            values = [self.stats[x][feature_ind+1] for x in labels]
            plt.bar(labels, values, width=0.2, color=(1, 0, 0, 0.5), align='center')
        plt.xlabel('Logos', fontweight='bold', color = 'orange', fontsize='17', horizontalalignment='center')
        plt.ylabel(feature, fontweight='bold', color = 'orange', fontsize='17', horizontalalignment='center')


    ##############################################################
    # calculate_rating()
    # This method calculates a rating for each logo based on the collected
    # statistics in self.stats, and it calls on plot_rated() to create a plot
    # of the top 10 rated logos.
    #
    # inputs: None
    # returns: None
    def calculate_rating(self):
        """
        - frequency should have the highest weight                 30%
        - area should be the seond highest rating                  25%
        - clarity comes third                                      25%
        - centratlity gets weighed more the more polys there are   20%
        """
        rating = {}
        for logo in self.stats.keys():
            frequency = self.stats[logo][0]
            clarity_mean = self.stats[logo][1]
            clarity_std = self.stats[logo][2]
            area_mean = self.stats[logo][3]
            area_std = self.stats[logo][4]
            cRating_mean = self.stats[logo][5]
            cRating_std = self.stats[logo][6]
            num_shared_logos = self.stats[logo][7]
            rating[logo] = 0.3*frequency + 0.25*area_mean*(1-area_std) + 0.25*clarity_mean*(1-clarity_std) + 0.2*(cRating_mean*num_shared_logos)
        values = []
        labels = []
        print(rating)
        for key in sorted(rating, key=rating.get, reverse=True)[:10]:
            values.append(rating[key])
            labels.append(key)
        self.plot_rated(values, labels)


    ##############################################################
    # plot_rated([double], [string])
    # This method creates a plot for the values and labels given, used by
    # calculate_rating to plot the top 10 rated logos.
    #
    # inputs: None
    # returns: None
    def plot_rated(self, values, labels):
        plt.figure()
        plt.bar(labels, values, width=0.1, color='b', align='center')
        plt.xlabel('Logos', fontweight='bold', color = 'orange', fontsize='17', horizontalalignment='center')
        plt.ylabel("Rating", fontweight='bold', color = 'orange', fontsize='17', horizontalalignment='center')



    ##############################################################
    # set_maxes(double, double)
    # This method sets self.max_area to the given area value if it is greater
    # than the instance variable, likewise for self.max_shared_logos.
    #
    # inputs: area, num_logos
    # returns: None
    def set_maxes(self, area, num_logos):
        if area > self.max_area:
            self.max_area = area
        if num_logos > self.max_shared_logos:
            self.max_shared_logos = num_logos


    ##############################################################
    # set_max_freq()
    # This method calculates the logo that has the max frequency, and sets
    # self.max_freq to the maximum frequency.
    #
    # inputs: None
    # returns: None
    def set_max_freq(self):
        for logo in self.mapping.keys():
            freq = len(self.mapping[logo])
            if freq > self.max_freq:
                self.max_freq = freq




if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.collect_data()
    analyzer.calculate_stats()
    analyzer.plot_for_feature()
    analyzer.calculate_rating()
    plt.show()

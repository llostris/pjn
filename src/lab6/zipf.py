from collections import defaultdict
from functools import reduce
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import operator
import re

__author__ = 'Magda'


class Zipf:

    def __init__(self, datafile, encoding='utf-8'):
        self.flexive_forms_file = '../../data/lab6/odm.txt'
        self.inflection_dict = {}
        self.forms_statistics = defaultdict(int)
        self.sorted_statistics = {}
        self.ignored_characters = r"[\.,:;!?()\\/0-9\"\-\'+]"
        self.unicode_characters = r"[\x84\x9a\x8f\x9d]"
        self.odm_ignored_characters = r"[\.\'\-]"

        self.hapax_legomena_num = 0
        self.fity_percent_num = 0

        self.ranks = None
        self.frequencies = None
        self.k = 1.0

        # initialize
        self.load_flexive_map()
        self.create_form_statistics(datafile, encoding)

    def load_flexive_map(self):
        with open(self.flexive_forms_file, encoding='iso-8859-2') as f:
            for line in f:
                # print("AAA:" + line)
                splitted = line.lower().strip().split(", ")
                base_form = splitted[0]
                for form in splitted:
                    form = form.rstrip()
                    form = re.sub(self.odm_ignored_characters, "", form)
                    self.inflection_dict[form] = base_form
            f.close()

        print('flexive dict: ', len(self.inflection_dict))

    def create_form_statistics(self, datafile, encoding) :
        with open(datafile, encoding=encoding) as f:
            for line in f:
                line = line.lower().strip()
                # line = re.sub(self.odm_ignored_characters, "", line)
                line = re.sub(self.ignored_characters, " ", line)
                line = re.sub(self.unicode_characters, " ", line)
                line = re.sub("\bframe\b", " ", line)
                splitted = line.split()
                for form in splitted:
                    if form in self.inflection_dict:
                        form = self.inflection_dict[form]
                    self.forms_statistics[form] += 1

        print(len(self.forms_statistics))
        print(self.forms_statistics)

        self.sorted_statistics = sorted(self.forms_statistics.items(), key=operator.itemgetter(1), reverse=True)
        print(self.sorted_statistics)
        self.forms_statistics = {}

    def initialize_ranks_and_frequencies(self):
        ranks = []
        frequencies = []
        rank = 1
        for (word, frequency) in self.sorted_statistics:
            ranks.append(float(rank))
            frequencies.append(float(frequency))
            rank += 1
        ranks = np.array(ranks, dtype=np.float64)
        frequencies = np.array(frequencies, dtype=np.float64)
        self.ranks = ranks
        self.frequencies = frequencies

    def find_k_constant(self):
        if self.ranks is None or self.frequencies is None:
            self.initialize_ranks_and_frequencies()

        def zipf(x, k):
            return k / x

        popt, pcov = curve_fit(zipf, self.ranks, self.frequencies, np.array([1.0], dtype=np.float64))
        self.k = popt[0]
        print(self.k)


    def mandelbrots(self, rank, p, b, d):
        return p / ((rank + d) ** b)

    def find_mandelbrots_constants(self):
        p = 40099.5082
        b = 1.22
        d = 0.971

        b = 1.28
        d = 30.971
        p = 404456.319495

        if self.ranks is None or self.frequencies is None:
            self.initialize_ranks_and_frequencies()

        self.frequencies = np.transpose(self.frequencies)
        self.ranks = np.transpose(self.ranks)

        popt, pcov = curve_fit(self.mandelbrots, self.ranks, self.frequencies, np.array([1.0, 0.00003, 0.00074],
                                                                                        dtype=np.float64))
        print(popt)
        # return(popt[0], popt[1], popt[2])
        return p, b, d

    def create_plot(self):
        plt.figure(0)
        handles = []
        legend = [ "Frequency","Zipf's", "Mandelbrot's"]
        plt.suptitle("Zipf's and Mandelbrot's laws")
        plt.ylabel("Frequency")
        plt.xlabel("Rank")
        plt.yscale('log', nonposy='clip')

        lines, = plt.plot(self.frequencies)
        handles.append(lines)

        zipfs = [ 1.0 * self.k / rank for rank in self.ranks]
        lines, = plt.plot(zipfs)
        handles.append(lines)

        p, b, d = self.find_mandelbrots_constants()
        mandelbrots = [self.mandelbrots(rank * 1.0, p, b, d) for rank in self.ranks ]
        lines, = plt.plot(mandelbrots)
        handles.append(lines)

        plt.legend(handles, legend)
        plt.show()

    def get_hapax_legomena(self):
        hapax_legomena = filter(lambda x: x[1] == 1, self.sorted_statistics)
        self.hapax_legomena_num = len(list(hapax_legomena))
        return self.hapax_legomena_num

    def get_fity_percent(self):
        total_words = reduce(lambda x, y: x + y[1], self.sorted_statistics, 0)
        half_total_words = total_words * 1.0 / 2
        print('in dictionary: ', len(self.sorted_statistics))
        print('total_words: ', total_words)

        fifty_percent_words = 0
        word_count = 0
        for (word, frequency) in self.sorted_statistics:
            word_count += frequency
            fifty_percent_words += 1
            if word_count >= half_total_words:
                break
        return fifty_percent_words


if __name__ == "__main__":
    zipf = Zipf('../../data/lab6/potop.txt')
    print('Hapax legomena: ', zipf.get_hapax_legomena())
    print('Number of distinct words that constitute 50% of text: ', zipf.get_fity_percent())
    zipf.find_k_constant()
    zipf.create_plot()

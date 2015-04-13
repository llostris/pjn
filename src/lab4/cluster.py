from functools import reduce
import math
import operator
import re
from lab1.ngram import NGramFinder

__author__ = 'Magda'

DATA_DIRECTORY = '../../data/lab4/'


class WordMetric:

    # @staticmethod
    def dice_metric(self, x, y):
        """
        Calculates dice distance between to vectors of ngrams.
        :param x: vector of ngrams of first string
        :param y: vector of ngrams of second string
        :return: double representing dice distance between first and second string
        """
        numerator = 2 * len(set(set(x.keys()).intersection(set(y.keys()))))
        denominator = len(x) + len(y)
        return 1 - 1.0 * numerator / denominator

    # @staticmethod
    def cosine_metric(self, x, y):
        """
        Calculates cosine distance between to vectors of ngrams.
        :param x: vector of ngrams of first string
        :param y: vector of ngrams of second string
        :return: double representing cosine distance between first and second string
        """
        keys = set(list(x) + list(y))
        distance = 0
        for ngram in keys:
            if ngram in x and ngram in y:
                distance += x[ngram] * y[ngram]

        norm = (self.norm(x.values()) * self.norm(y.values()))
        if norm == 0 :
            norm = 1
        distance = 1.0 * distance / norm
        return 1 - distance

    def lcs_metric(self, x, y):
        """
        Calculates longest common substring between two strings
        :param x: string
        :param y: string
        :return: double, LCS
        """

        nominator = len(self.longest_common_substring(x, y))
        denominator = max(len(x), len(y))
        return 1 - nominator / denominator

    def longest_common_substring(self, s1, s2):
        tab = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
        longest, x_longest = 0, 0

        for x in range(1, 1 + len(s1)):
            for y in range(1, 1 + len(s2)):
                if s1[x - 1] == s2[y - 1]:
                    tab[x][y] = tab[x - 1][y - 1] + 1
                    if tab[x][y] > longest:
                        longest = tab[x][y]
                        x_longest = x
                else:
                    tab[x][y] = 0

        return s1[x_longest - longest: x_longest]

    def norm(self, vector):
        value = reduce(lambda x, y: x + y ** 2, vector, 0)
        return math.sqrt(value)


class Clusterizer:

    def __init__(self, datafile, result_file=DATA_DIRECTORY + 'clusters_my.txt', maximum_distance=0.3):
        self.metrics = WordMetric()
        self.ngram_finder = NGramFinder(2)
        self.ignored_characters = r"[\.:;,!\?\"\-'\\/+()0-9]"
        self.datafile = datafile
        self.result_file = result_file
        self.cluster_file = DATA_DIRECTORY + 'clusters.txt'
        self.stoplist_file = DATA_DIRECTORY + 'stoplist.txt'
        self.countries_file = DATA_DIRECTORY + 'countries.txt'
        self.forms = {}
        self.stoplist = set()
        self.original_data = {}
        self.maximum_distance = maximum_distance

        self.data = []
        self.clusters = []

        self.separator = "##########"

        # self.load_data()

    def load_data(self):
        with open(self.stoplist_file) as f:
            for line in f.readlines():
                self.stoplist.add(line.strip())

        with open(self.datafile) as f:
            for line in f.readlines():
                stripped = self.prepare_string(line)
                # print(stripped)
                stripped = filter(lambda x: not x in self.stoplist, stripped.split())
                stripped = " ".join(stripped)
                self.data.append(stripped)
                self.original_data[line.strip()] = self.ngram_finder.get_ngrams(stripped)
                # print(stripped, "____", line)
                # print(line, self.original_data[line.strip()])

    def create_stoplist(self):
        # add most populr words in dataset
        with open(self.datafile) as f:
            for line in f.readlines():
                line = self.prepare_string(line)
                for word in line.split():
                    if word in self.forms:
                        self.forms[word] += 1
                    else:
                        self.forms[word] = 0

        # additional modifications
        self.forms.pop("panalpina")
        self.forms.pop("schenker")

        stoplist = sorted(self.forms.items(), key=operator.itemgetter(1), reverse=True)

        stopwords = [ 'and', 'or', 'for', 'on' ]

        print(stoplist[:60])

        with open(self.stoplist_file, 'w') as f:
            for word in stoplist[:100]:
                f.write(word[0] + '\n')

            # # add countries
            # with open(self.countries_file) as fcountry:
            #     for line in fcountry.readlines():
            #         f.write(line[3:].strip().lower() + '\n')
            # f.close()
            #
            # for word in stopwords:
            #     f.write(word + '\n')

        self.forms = {} # clear memory

    def prepare_string(self, text):
        line = re.sub(self.ignored_characters, "", text)    # remove unnecessary characters
        line = " ".join(line.split()).lower().strip()       # remove double spaces
        return line

    def clusterize(self):
        with open(self.result_file, 'w') as f:
            f.truncate(0)
            f.close() # clear file

        while len(self.original_data) > 0:
            first_cluster = self.original_data.popitem()
            cluster = [ first_cluster[0] ]
            # print(first_cluster)
            for line in self.original_data:
                # print(self.metrics.cosine_metric(first_cluster[1], self.original_data[line]) , line)
                if self.metrics.cosine_metric(first_cluster[1], self.original_data[line]) < self.maximum_distance:
                    cluster.append(line)

            for line in cluster:
                if line in self.original_data:
                    self.original_data.pop(line)

            # self.clusters.append(cluster)
            with open(self.result_file, 'a') as f:
                for line in cluster:
                    f.write(line + "\n")
                f.write("\n" + self.separator + "\n")
                f.close()


if __name__ == "__main__":
    clusterizer = Clusterizer(DATA_DIRECTORY + 'lines.txt')
    # clusterizer.create_stoplist()
    clusterizer.load_data()
    clusterizer.clusterize()
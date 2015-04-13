__author__ = 'Magdalena Strzoda'

from sys import argv
from os import listdir
from os.path import isfile, join
from lab1.ngram import NGramFinder, NGramStatistics
import re

DEFAULT_TEXT_CORPUS_DIRECTORY = '../../data/pjn_lab1/'

filenames = [ "Harry Potter 1 Sorcerer's_Stone.txt"]

INTERPUNCTION_REGEXP = r"[\.:;,!\?\"]"

DEFAULT_N = 2


def statistics(n, directory):
    # filenames = [ filename for filename in listdir(directory) if isfile(join(directory, filename)) ]
    statistics_map = {}
    for filename in filenames:
        print(filename)
        with open(join(directory, filename)) as f:
            lines = f.read()
            stats = NGramStatistics(NGramFinder(n))
            stats.analyze(lines)
            print(stats.statistics)

    return statistics_map

if __name__ == '__main__':

    directory = DEFAULT_TEXT_CORPUS_DIRECTORY
    n = DEFAULT_N

    if len(argv) > 1 :
        directory = argv[1]
    if len(argv) > 2 :
        n = int(argv[2])

    statistics(n, directory)


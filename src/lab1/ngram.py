import os
import re
from os import listdir
from os.path import isfile, join

__author__ = 'Magda'


class NGramFinder:

    def __init__(self, n):
        self.n = n
        self.interpuction_regexp = r"[\.:;,!\?\"]"

    def get_ngrams(self, corpus):
        corpus = re.sub(self.interpuction_regexp, "", corpus)
        words = corpus.split()
        ngrams = {}
        for word in words:
            for index in range(len(word) - self.n):
                gram = word[index : index + self.n]
                if gram in ngrams:
                    ngrams[gram] += 1
                else:
                    ngrams[gram] = 1
        return ngrams

    def get_word_1grams(self, corpus):
        corpus = re.sub(self.interpuction_regexp, "", corpus)
        words = corpus.split()
        ngrams = {}
        for word in words:
            if word in ngrams:
                ngrams[word] += 1
            else:
                ngrams[word] = 1
        return ngrams

    def get_word_ngrams(self, corpus):
        corpus = re.sub(self.interpuction_regexp, "", corpus)
        words = corpus.split()
        ngrams = {}
        for index in range(len(words) - self.n):
                gram = words[index : index + self.n]
                gram = " ".join(gram)
                if gram in ngrams:
                    ngrams[gram] += 1
                else:
                    ngrams[gram] = 1
        return ngrams


class NGramStatistics:

    def __init__(self, ngram, language=None):
        self.ngram = ngram
        self.language = language
        self.statistics = {}
        self.frequency = []

    def analyze(self, corpus):
        word_map = self.ngram.get_ngrams(corpus)

        # add the word map to existing word statistics
        for word in word_map:
            if word in self.statistics:
                self.statistics[word] += word_map[word]
            else:
                self.statistics[word] = word_map[word]

        return self     # allows for method chaining

    def get_statistics(self):
        return self.language, self.statistics


class LanguageStatistics:

    def __init__(self, n):
        self.ngram_finder = NGramFinder(n)
        self.language_map = {}
        self.numeric_characters_regexp = r"[0-9]"

    def get_language(self, filename):
        filename_without_extension = os.path.splitext(filename)[0]
        return re.sub(self.numeric_characters_regexp, "", filename_without_extension.lower())

    def analyze_directory_dataset(self, directory):
        filenames = [ filename for filename in listdir(directory) if isfile(join(directory, filename)) ]

        for filename in filenames:
            with open(join(directory, filename)) as f:
                language = self.get_language(filename)
                print(language)
                lines = f.read()

                if language in self.language_map:
                    self.language_map[language].analyze(lines)
                else:
                    statistics = NGramStatistics(self.ngram_finder, language)
                    statistics.analyze(lines)
                    self.language_map[language] = statistics
        self.sort_by_frequency()

    def sort_by_frequency(self):
        for language in self.language_map:
            ngram_map = self.language_map[language].statistics
            self.language_map[language].frequency = sorted(ngram_map, key=lambda key: ngram_map[key], reverse=True)
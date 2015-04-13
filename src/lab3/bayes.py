from collections import OrderedDict
import re
import math
from lab2.levenshtein import SpellChecker

__author__ = 'Magda'


DATA_DIRECTORY = '../../data/lab3/'
ERROR_FILE = 'bledy.txt'
FORMS_FILE = 'formy.txt'
CORPUSES = [ 'dramat.iso.utf8', 'popul.iso.utf8', 'proza.iso.utf8', 'publ.iso.utf8', 'wp.iso.utf8' ]

class BayesSpellChecker:

    def __init__(self, corpus='dramat.iso.utf8'):
        self.spell_checker = SpellChecker(data_source=None) # used only in order to not-reimplement functions
        self.prompt = 'Please enter a word: '
        self.interpunction_regexp = r"[\.:;,!\?\"'*\-0-9]"

        self.forms = set()
        self.errors = {}
        self.distances = {}
        self.distance_map = {}
        self.probabilities = {}

        self.default_distance = 1.0

        # statistics made from corpus
        self.form_statistics = {}
        self.words_in_corpus = 0

        self.corpus = corpus
        self.available_forms_number = 0
        self.errors_number = 0

        self.load_data()
        self.generate_error_model()
        for corpus in CORPUSES:
            self.gather_statistics(corpus)
        print(self.distance_map)

    def load_data(self):
        # with open(DATA_DIRECTORY + FORMS_FILE, encoding='iso-8859-2') as f:
        #     for line in f.readlines() :
        #         word = line.strip()
        #         if word in self.form_statistics:
        #             self.form_statistics[word] += 1
        #         else:
        #             self.form_statistics[word] = 1
        #
        # f.close()

        with open(DATA_DIRECTORY + ERROR_FILE, encoding='utf-8') as f:
            for line in f.readlines():
                splitted = line.split(";")
                self.errors[splitted[0]] = splitted[1].strip()
        f.close()
        self.distance_map2 = sorted(self.distance_map.items(), key=lambda t: t[1])
        # print self.distance_map2
        # print(self.errors)

    def levenshtein_distance(self, word1, word2):
        # return self.spell_checker.levenshtein_distance(word1, word2)
        return self.spell_checker.levenshtein_correction(word1, word2)

    def gather_statistics(self, corpus):
        with open(DATA_DIRECTORY + corpus, encoding='utf-8') as f:
            for line in f.readlines():
                line = re.sub(self.interpunction_regexp, "", line)
                splitted = [ i.strip() for i in line.split() ]
                for word in splitted:
                    if True:
                    # if len(word) > 3:
                        word = word.lower()
                        if word in self.form_statistics:
                            self.form_statistics[word] += 1
                        else:
                            self.form_statistics[word] = 1
                self.words_in_corpus += 1

        print(self.form_statistics)
        # print(self.words_in_corpus)

    # levenshtein-heavy version

    def generate_error_model(self):
        for error in self.errors:
            distance = self.levenshtein_distance(error, self.errors[error])
            if distance in self.distance_map:
                self.distance_map[distance] += 1
            else:
                self.distance_map[distance] = 1
            self.errors_number += 1

    def probability(self, word, correction):
        distance = self.levenshtein_distance(word, correction)
        # print(distance)
        if  distance in self.distance_map:
            return self.distance_map[distance] / self.errors_number
        return 0
        # return 1 - (1.0 * distance / max(len(word), len(correction)) ) * self.default_distance


    # probabilistic -> error model

    def bayes_probability(self, word, correction):
        p_w_c = self.probability(word, correction)
        # return p_w_c

        if correction in self.form_statistics:
            form_occurrences = self.form_statistics[correction]
        else:
            form_occurrences = 0
        p_c = (1 + form_occurrences) * 1.0 / (len(self.form_statistics) + (self.words_in_corpus))

        bayes_probability = p_c * p_w_c
        # print('P(w|c)', p_w_c)
        # print('P(c)', p_c)
        # print('P(c|w)', bayes_probability)
        return bayes_probability


    def get_correction(self, word):
        best_correction = word
        if word in self.errors:
            best_correction = self.errors[word]
        best_probability = 0

        for correction in self.form_statistics:
            probability = self.bayes_probability(word, correction)
            if probability > best_probability:
                best_probability = probability
                best_correction = correction

        return best_correction, best_probability

    def start(self):
        while True:
            word = input(self.prompt)
            word = word.strip().lower()
            print(self.get_correction(word))

    def test(self):
        right = 0
        wrong = 0
        for error in self.errors:
            correction = self.get_correction(error)
            print(error, correction)
            if correction == self.errors[error]:
                right += 1
            else:
                wrong += 1
        print('Right %d Wrong %d', right, wrong)


if __name__ == "__main__":

    spellchecker = BayesSpellChecker()

    print(spellchecker.bayes_probability("apsolutnie", "absolutnie"))
    print(spellchecker.bayes_probability("apsolutnie", "abazur"))
    # spellchecker.test()
    spellchecker.start()
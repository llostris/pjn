import math
from lab1.ngram import NGramFinder, LanguageStatistics


__author__ = 'Magda'


DEFAULT_TEXT_CORPUS_DIRECTORY = '../../data/lab1/'


class LanguageFinder:

    def __init__(self, n=2):
        self.ngram_finder = NGramFinder(n)
        self.language_statistics = LanguageStatistics(n)
        self.language_statistics.analyze_directory_dataset(DEFAULT_TEXT_CORPUS_DIRECTORY)

        self.prompt_text = "Type a phrase in any of the languages: Finnish, English, Polish, Spanish, Italian, " \
                           "German. \n>> "

    def analyze_sentence(self, sentence):
        vector = self.ngram_finder.get_ngrams(sentence)
        # self.rank_languages_order(vector)
        self.rank_languages_cosine(vector)

    def rank_languages_order(self, vector):
        # print vector
        vector_ordered = sorted(vector, key=lambda key: vector[key], reverse=True)
        # print vector_ordered
        language_distance_map = {}
        for language in self.language_statistics.language_map:
            frequency = self.language_statistics.language_map[language].frequency
            # print frequency
            out_of_place_distance = 0
            for ngram in vector_ordered:
                if ngram in frequency:
                    out_of_place_distance += abs(vector_ordered.index(ngram) - frequency.index(ngram))
                else:
                    out_of_place_distance += len(frequency)
                    pass     # what to do?

            language_distance_map[language] = out_of_place_distance
            # print language, out_of_place_distance

        language_order = sorted(language_distance_map.items(), key=lambda x: x[1])
        for language in language_order:
            language = language[0]
            print(language, language_distance_map[language])

    def rank_languages_cosine(self, vector):
        # print vector_ordered
        language_distance_map = {}
        for language in self.language_statistics.language_map:
            distance = self.cosine_distance(self.language_statistics.language_map[language].statistics, vector)
            language_distance_map[language] = distance
            # print language, out_of_place_distance

        language_order = sorted(language_distance_map.items(), key=lambda x: x[1], reverse=True)
        for language in language_order:
            language = language[0]
            print(language, language_distance_map[language])

    def cosine_distance(self, vec1, vec2):
        # keys = set(vec1.keys() + vec2.keys()) # python 2.7 version
        keys = set(list(vec1) + list(vec2))
        distance = 0
        for ngram in keys:
            if ngram in vec1 and ngram in vec2:
                distance += vec1[ngram] * vec2[ngram]

        norm = (self.norm(vec1.values()) * self.norm(vec2.values()))
        if norm == 0 :
            norm = 1
        distance = distance / norm
        return distance

    def euclidean_distance(self, vec1, vec2):
        keys = set(vec1.keys() + vec2.keys())
        distance = 0
        for ngram in keys:
            try:
                distance += (vec1[ngram] - vec2[ngram]) ** 2
                print(distance)
            except KeyError:
                pass    # add 0

        distance = math.sqrt(distance)
        return distance

    def norm(self, vector):
        value = 0
        for i in vector:
            value += i * i
        return math.sqrt(value)

    def start(self):

        while True:

            data = input(self.prompt_text)
            self.analyze_sentence(data)


if __name__ == "__main__":

    LanguageFinder(3).start()
from collections import defaultdict
import operator
import pickle
import re
import math
from lab4.cluster import WordMetric

__author__ = 'Magda'

class VectorRepresentation:

    def __init__(self, flexive_forms_file='../../data/odm.txt', notes_file='../../data/pap.txt', encoding='utf-8',
                 initialized=False):
        self.inflection_dict = {}
        self.term_frequency = {}
        self.document_frequency = defaultdict(int)
        self.df_idf_matrix = defaultdict(int)
        self.keyword_map = {}
        self.note_number = 0
        self.word_metric = WordMetric()
        self.max_value = 0
        self.min_value = 100.0

        self.ignored_characters = r"[\.,:;!?()\\/0-9\"\-\'+]"
        self.odm_ignored_characters = r"[\.\'\-]"

        self.idf_matrix_file = '../../data/lab7/matrix.pickle'
        self.inflection_file = '../../data/lab7/inflection.pickle'

        self.load_flexive_map(flexive_forms_file)
        self.initialize_data(notes_file, encoding)
        self.build_df_idf_matrix()
        self.find_keywords(7)

    # initialization

    def load_flexive_map(self, flexive_forms_file):
        with open(flexive_forms_file, encoding='iso-8859-2') as f:
            for line in f:
                # print("AAA:" + line)
                splitted = line.lower().strip().split(", ")
                base_form = splitted[0]
                for form in splitted:
                    form = form.rstrip()
                    form = re.sub(self.odm_ignored_characters, "", form)
                    self.inflection_dict[form] = base_form
            f.close()
        print("Flexive form map loaded")

        pickle.dump(self.inflection_dict, open(self.inflection_file, 'wb'))

    def initialize_data(self, notes_file, encoding):
        term_frequency = {}
        note_id = -1
        with open(notes_file, encoding=encoding) as f:
            for line in f:
                if line.startswith("#"):
                    if note_id != -1:
                        # print(term_frequency)
                        # print(note_id)
                        self.term_frequency[note_id] = term_frequency

                    note_id = int(line[1:])
                    self.note_number += 1
                    term_frequency = defaultdict(int)
                else:
                    line = line.lower().strip()
                    line = re.sub(self.ignored_characters, " ", line)
                    splitted = line.split()
                    for term in splitted:
                        if term in self.inflection_dict:
                            term = self.inflection_dict[term]

                        self.document_frequency[term] += 1
                        term_frequency[term] += 1

        # self.inflection_dict = None # free memory

        print("Loaded %d notes" % self.note_number)

    def build_df_idf_matrix(self):
        for note_id in self.term_frequency:
            matrix = {}
            term_frequencies = self.term_frequency[note_id]
            for term in term_frequencies:
                matrix[term] = term_frequencies[term] * math.log(float(self.note_number) / self.document_frequency[term])
                if matrix[term] > self.max_value:
                    self.max_value = matrix[term]
                if matrix[term] < self.min_value:
                    self.min_value = matrix[term]
            # print(matrix)
            self.df_idf_matrix[note_id] = matrix
            self.term_frequency[note_id] = None # free memory

        self.term_frequency = {}
        print('Max/Min:', self.max_value, self.min_value)
        pickle.dump(self.df_idf_matrix, open(self.idf_matrix_file, "wb" ))

    def find_keywords(self, n):
        for note_id in self.df_idf_matrix:
            sorted_terms = sorted(self.df_idf_matrix[note_id].items(), key=operator.itemgetter(1), reverse=True)
            # print(sorted_terms)
            sorted_terms = list(filter(lambda x: x[1] > 3.0, sorted_terms))
            # print(sorted_terms)
            keywords = self.get_column(sorted_terms[:n], 0)
            self.keyword_map[note_id] = keywords
            # print(keywords)

    @staticmethod
    def get_column(array, index):
        """
        Extracts a column from 2-dimensional array.
        :param array: 2-dimensional array, an array of tuples etc.
        :param index: Index of column to extract
        """
        column = []
        for row in array:
            column.append(row[index])
        return column

    def find_document_by_keywords(self, keywords):
        best_matches = []
        best_match_id = 0
        best_score = 0
        for note_id in self.df_idf_matrix:
            score = 0
            for keyword in keywords:
                if keyword in self.keyword_map[note_id]:
                    score += self.df_idf_matrix[note_id][keyword]
                if score > best_score:
                    # best_matches.append(note_id)
                    best_score = score
                    best_match_id = note_id
        print(best_match_id, best_score)
        return best_match_id

    def find_similar_document(self, document):
        term_frequency_vector = defaultdict(int)

        document = document.lower().strip()
        document = re.sub(self.ignored_characters, " ", document)
        splitted = document.split()
        for term in splitted:
            if term in self.inflection_dict:
                term = self.inflection_dict[term]
            term_frequency_vector[term] += 1

        vector = {}
        for term in term_frequency_vector:
            vector[term] = term_frequency_vector[term] * math.log(float(self.note_number) / self.document_frequency[term])

        closest_distance = 100000.0     # infinity
        closest_document_id = 0
        for note_id in self.df_idf_matrix:
            distance = self.word_metric.cosine_metric(self.df_idf_matrix[note_id], vector)
            # print(distance)
            if distance < closest_distance:
                closest_distance = distance
                closest_document_id = note_id

        # print(closest_document_id)
        return closest_document_id
    # additional functions

    def run(self):
        main_menu_string = "\nType:\n\t" \
                "1 - find note by keywords\n\t" \
                "2 - find note by another note\n\t" \
                "3 - show keywords for note id\n--------\n"

        while True:
            print(main_menu_string)
            data = input(">> ")

            if data == "1":
                keywords = input("Type keywords separated by space characters: ")
                found = self.find_document_by_keywords(keywords.split())
                print("Best match is note: #%d" % found)
                print(self.df_idf_matrix[found])
            elif data == "2":
                note = input("Type your note: ")
                found = self.find_similar_document(note)
                print("Best match is note: #%d" % found)
                print(self.df_idf_matrix[found])
            elif data == "3":
                note_id = input("Type your note id: ")
                print("Keywords are: ", self.keyword_map[int(note_id)])
            else:
                print("Invalid choice")


if __name__ == "__main__":

    vector = VectorRepresentation()
    vector.run()
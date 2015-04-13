# coding=utf-8

__author__ = 'Magda'

DATA_DIRECTORY = '../../data/lab2/'

class SpellChecker :

    def __init__(self, data_source='prefix') :
        self.prompt_text = 'Type two words separated by a space:\n>> '
        self.spell_checker_prompt_text = 'Type a word:\n>> '

        self.cost_insertion = 1
        self.cost_deletion = 1
        self.cost_substitution = 1                  # any other substitution
        self.cost_substitution_orthographic = 0.25  # fix orthographic errors first
        self.cost_substitution_diacritic = 0.25     # fix problems with diacritic character
        self.cost_swap = 0.5                       # fix problems with 'Czech errors', like kapr - karp etc.

        self.dictionary = set()
        self.prefixes = {}
        self.suffixes = {}

        self.ortography_map = {
            'u' : 'ó',
            'ó' : 'u',
            'ch' : 'h',
            'h' : 'ch',
            'rz' : 'ż',
            'ż' : 'rz'
        }
        self.diacritic_map = {
            'a' : 'ą', 'c' : 'ć', 'e' : 'ę', 'l' : 'ł', 'n' : 'ń', 'o' : 'ó', 's' : 'ś', 'z' : ('ż', 'ź'),
        }
        self.z_key = 'z'    # the only key that can be resolved in two ways, so it is kind of a problematic one

        self.data_source = data_source
        if self.data_source != None:
            if self.data_source == 'dictionary':
                self.load_data()
            else:
                self.load_pref_suf()



    def load_data(self) :
        with open(DATA_DIRECTORY + 'formy.txt', encoding='iso-8859-2') as f:
            dictionary = f.readlines()
            for line in dictionary :
                self.dictionary.add(line.strip())

    def load_pref_suf(self):
        self.load_prefixes()
        self.load_suffixes()

    def load_prefixes(self):
        with open(DATA_DIRECTORY + 'pocz.dat', encoding='iso-8859-2') as f:
            for line in f.readlines():
                data = line.split(":")
                if data[0] not in self.prefixes:
                    self.prefixes[data[0]] = []
                if len(data) > 1:
                    self.prefixes[data[0]].append(int(data[1].strip()))

    def load_suffixes(self):
        with open(DATA_DIRECTORY + 'konc.dat', encoding='iso-8859-2') as f:
            for line in f.readlines():
                data = line.split(";")
                suffixes = map(lambda x: x.strip(), data[2].split(":"))
                suffixes = filter(lambda x: len(x) > 0, suffixes)
                self.suffixes[int(data[0])] = suffixes

    def is_orthographic_error(self, word1, word2, ind1, ind2):
        return word1[ind1] in self.ortography_map and self.ortography_map[word1[ind1]] == word2[ind2]

    def is_diacritic_error(self, word1, word2, ind1, ind2):
        return word1[ind1] in self.diacritic_map and (self.diacritic_map[word1[ind1]] == word2[ind2] or
                                                                    word2[ind2] in self.diacritic_map[self.z_key])

    def is_czech_error(self, word1, word2, ind1, ind2):
        first = ind1 < len(word1) - 1 and ind2 < len(word2) - 1 and word1[ind1] == word2[ind2 + 1] \
                and word1[ind1 +  1] == word2[ind2]
        second = ind1 > 0 and ind2 > 0 and word1[ind1 - 1] == word2[ind2] and word1[ind1] == word2[ind2 -1]
        return first or second

    def levenshtein_distance(self, word1, word2) :
        tab = [ [0 for _ in range(len(word1) + 1) ] for _ in range(len(word2) + 1)]

        for i in range(len(word2)) :
            tab[i][0] = i
        for i in range(len(word1)) :
            tab[0][i] = i

        # print(tab)
        for j in range(1, len(word1), 1) :
            for i in range(1, len(word2), 1) :
                if word1[j] == word2[i] :
                    cost = 0
                else :
                    cost = 1
                tab[i][j] = min(tab[i - 1][ j] + 1,
                                tab[i][ j - 1] + 1,
                                tab[i - 1][j - 1] + cost
                                )

        # self.print_tab(tab)
        return tab[len(word2) - 1][len(word1) - 1]

    def map_word(self, word):
        ind = 0
        tab = []
        while ind < len(word) - 1:
            if word[ind:ind+2] in self.ortography_map:
                tab.append(word[ind:ind+2])
                ind += 2
            else:
                tab.append(word[ind])
                ind += 1
        if ind < len(word):
            tab.append(word[ind])
        return tab

    def levenshtein_correction(self, word1, word2, max_distance=10) :
        if abs(len(word1) - len(word2)) > 2:
            return max(len(word1), len(word2))
        # word1 = self.map_word(word1)
        # word2 = self.map_word(word2)

        INF = len(word1) + len(word2)

        tab = [ [INF for _ in range(len(word1) + 1) ] for _ in range(len(word2) + 1)]

        for ind2 in range(len(word2)) :
            tab[ind2][0] = ind2 * 1.0
        for ind2 in range(len(word1)) :
            tab[0][ind2] = ind2 * 1.0

        cost = 0

        for ind1 in range(len(word1)) :
            for ind2 in range(len(word2)) :
                # print(word1[ind1], word2[ind2])
                insertion_deletion_cost = self.cost_insertion
                if word2[ind2] == word1[ind1] :
                    cost = 0
                    if ind1 > 1 and word1[ind1 - 1:ind1 + 1] in self.ortography_map and \
                        self.ortography_map[word1[ind1- 1:ind1 + 1]] == word2[ind2] :
                        insertion_deletion_cost = self.cost_substitution_orthographic
                    elif ind2 > 1 and word2[ind2 - 1:ind2 + 1] in self.ortography_map and \
                        self.ortography_map[word2[ind2 - 1:ind2 + 1]] == word1[ind1] :
                        insertion_deletion_cost = self.cost_substitution_orthographic
                    elif ind1 + 1 < len(word1) and word1[ind1:ind1 + 2] in self.ortography_map and \
                            self.ortography_map[word1[ind1:ind1 + 2]] == word2[ind2] :
                        insertion_deletion_cost = self.cost_substitution_orthographic
                    elif ind2 + 1 < len(word2) and word2[ind2:ind2 + 2] in self.ortography_map and \
                            self.ortography_map[word2[ind2:ind2 + 2]] == word1[ind1] :
                        insertion_deletion_cost = self.cost_substitution_orthographic
                else :
                    # if self.is_orthographic_error(word1, word2, ind1, ind2) :
                    if word1[ind1] in self.ortography_map and self.ortography_map[word1[ind1]] == word2[ind2] :
                        cost = self.cost_substitution_orthographic
                    # ch -> h, h -> ch
                    elif ind1 + 1 < len(word1) and word1[ind1:ind1 + 2] in self.ortography_map and \
                            self.ortography_map[word1[ind1:ind1 + 2]] == word2[ind2] :
                        cost = self.cost_substitution_orthographic
                    elif ind2 + 1 < len(word2) and word2[ind2:ind2 + 2] in self.ortography_map and \
                            self.ortography_map[word2[ind2:ind2 + 2]] == word1[ind1] :
                        cost = self.cost_substitution_orthographic
                    # rz -> ż, ż -> rz
                    elif ind1 > 0 and word1[ind1 - 1:ind1 + 1] in self.ortography_map and \
                        self.ortography_map[word1[ind1- 1:ind1 + 1]] == word2[ind2] :
                        cost = self.cost_substitution_orthographic
                        insertion_deletion_cost = self.cost_substitution_orthographic
                    elif ind2 > 0 and word2[ind2 - 1:ind2 + 1] in self.ortography_map and \
                        self.ortography_map[word2[ind2 - 1:ind2 + 1]] == word1[ind1] :
                        cost = self.cost_substitution_orthographic
                        insertion_deletion_cost = self.cost_substitution_orthographic
                    # diacritic errors
                    # elif self.is_diacritic_error(word1, word2, ind1, ind2) :
                    elif word1[ind1] in self.diacritic_map and (self.diacritic_map[word1[ind1]] == word2[ind2] or
                                                                    word2[ind2] in self.diacritic_map[self.z_key]):
                        cost = self.cost_substitution_diacritic
                    # Czech errors
                    # elif self.is_czech_error(word1, word2, ind1, ind2):
                    elif ind1 < len(word1) - 1 and ind2 < len(word2) - 1 and word1[ind1] == word2[ind2 + 1] \
                            and word1[ind1 +  1] == word2[ind2]:
                        cost = self.cost_swap
                    elif ind1 > 0 and ind2 > 0 and word1[ind1 - 1] == word2[ind2] and word1[ind1] == word2[ind2 -1]:
                        cost = self.cost_swap
                    else:
                        cost = self.cost_substitution

                # print('cost:', ind1, word1[ind1], ind2, word2[ind2], cost)
                tab[ind2+1][ind1+1] = min(
                                tab[ind2][ind1 + 1] + insertion_deletion_cost,
                                tab[ind2 + 1][ind1] + insertion_deletion_cost,
                                tab[ind2][ind1] + cost
                                )
                # print(tab[ind2][ind1 + 1] + insertion_deletion_cost,
                #                 tab[ind2 + 1][ind1] + insertion_deletion_cost,
                #                 tab[ind2][ind1] + cost)

        # self.print_tab(tab)
        return tab[len(word2)][len(word1)]

    def check_spelling(self, word):
        lowest_score = 1000
        corrected_word = []

        for word2 in self.dictionary:
            if True:
            # if word[0] == word2[0]  or (word[0] in self.diacritic_map and (self.diacritic_map[word[0]] == word2[0] or
            #     word2[0] in self.diacritic_map[self.z_key])) or word[0] in self.ortography_map \
            #     and (word2[0] == self.ortography_map[word[0]] or word2[:2] ==self.ortography_map[word[0]]) :
                score = self.levenshtein_correction(word, word2, lowest_score)
                if score < lowest_score:
                    lowest_score = score
                    # corrected_word = word2
                    corrected_word = []
                if score == lowest_score:
                    corrected_word.append((word2, score))

                if lowest_score < 0.1:
                    break   # can't be lower

                # print(lowest_score, corrected_word)

        return corrected_word

    def check_spelling_prefix(self, word):
        lowest_score = 1000
        corrected_word = ''

        self.suffixes = {}
        self.load_suffixes()

        for prefix in self.prefixes:
            # if True:
            if prefix[0] == word[0] or (word[0] in self.diacritic_map and (self.diacritic_map[word[0]] == prefix[0] or
                                            prefix[0] in self.diacritic_map[self.z_key])) or word[0] in \
                    self.ortography_map and (prefix[0] == self.ortography_map[word[0]] or prefix[:2] ==
            self.ortography_map[word[0]]):
                prefix_set = self.prefixes[prefix]
                for index in prefix_set:
                    if index != -1:
                        for suffix in self.suffixes[index]:
                            word2 = prefix + suffix
                            score = self.levenshtein_correction(word, word2, lowest_score)
                            if score < lowest_score:
                                lowest_score = score
                                corrected_word = word2

                        if lowest_score < 0.1:
                            return corrected_word, lowest_score   # can't be lower

        return corrected_word, lowest_score

    def start_comparison(self):
        while True:
            data = input(self.prompt_text)
            words = data.split()
            print(words)
            print(self.levenshtein_distance(words[0], words[1]))
            print(self.levenshtein_correction(words[0], words[1]))

    def start(self):
        while True:
            data = input(self.spell_checker_prompt_text)

            if self.data_source == 'dictionary':
                print(self.check_spelling(data))
            else:
                print(self.check_spelling_prefix(data))

    def print_tab(self, tab):
        for i in range(len(tab)):
            print(tab[i])


if __name__ == "__main__":

    spell_checker = SpellChecker('dictionary')
    # spell_checker = SpellChecker('prefix')

    # spell_checker.start()
    spell_checker.start_comparison()
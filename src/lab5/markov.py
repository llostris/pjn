from collections import defaultdict
import os
import pickle
import random
import re
from lab1.ngram import NGramFinder


__author__ = 'Magda'


DATA_DIRECTORY = '../../data/lab5/'
TYPE_WORD = "word"
TYPE_LETTER = "letter"
ALLOWED_TYPES = [ TYPE_LETTER, TYPE_WORD]


class MarkovChain:

    def __init__(self, type, corpus_file, n=2, reload=False):
        if not self.validate_arguments(type):
            print("Invalid call. Type should be one of: " + ", ".join(ALLOWED_TYPES))
            return

        self.n = n
        self.key = n - 1
        self.type = type
        self.corpus_file = corpus_file
        self.ngram_finder = NGramFinder(n)
        self.word_ngrams = defaultdict(int)
        self.letter_ngrams = defaultdict(int)
        self.word_chain = {}
        self.letter_chain = {}
        self.chain_filename_suffix = "_chain.pickled"
        self.chain_filename_prefix = type + str(n)

        self.ignored_characters = r"[0-9]"
        self.ignored_characters = r"[\"\-'\\/+()]"   #.;:,?!
        self.letter_ignored_characters = r"[\.:;,`!\?\"\-'\\/+()0-9]"

        self.initialize_chain(type, reload)

    def validate_arguments(self, type):
        if not type in ALLOWED_TYPES:
            return False
        return True

    def initialize_chain(self, type, reload):
        if not reload and os.path.isfile(type + self.chain_filename_suffix):
            self.load_chain(type)
        else:
            if type == TYPE_WORD:
                self.load_data()
            else:
                self.load_letter_data()

    def load_chain(self, type):
        print("loading chain")
        filename = type + self.chain_filename_suffix
        chain = pickle.load(open(filename, 'rb'))
        if type == 'word':
            self.word_chain = chain
        else:
            self.letter_chain = chain

    def load_data(self):
        print("loading data")
        with open(self.corpus_file, encoding='utf-8') as f:
            data = ""
            for line in f.readlines():
                if not line.startswith("#"):
                    data += line
                else:
                    line = re.sub(self.ignored_characters, "", data).lower()
                    ngrams = self.get_word_ngrams(line)
                    for ngram in ngrams:
                        self.word_ngrams[ngram] += ngrams[ngram]
                    data = ""
            f.close()

        for ngram in self.word_ngrams:
            splitted = ngram.split()
            prefix = " ".join(splitted[:self.key])
            if prefix not in self.word_chain:
                self.word_chain[prefix] = [ ]
            suffix = " ".join(splitted[self.key:])
            for i in range(self.word_ngrams[ngram]):
                self.word_chain[prefix].append(suffix)

        pickle.dump(self.word_chain, open(self.type + self.chain_filename_suffix, "wb" ))

        # print(self.word_ngrams)

    def load_letter_data(self):
        print("loading data")
        encoding = 'iso-8859-2'
        # encoding = 'utf-8'
        with open(self.corpus_file, encoding=encoding) as f:
        # with open(self.corpus_file, encoding='utf-8') as f:
            for line in f.readlines():
                if not line.startswith("#"):
                    line = re.sub(self.letter_ignored_characters, "", line.lower())
                    ngrams = self.ngram_finder.get_ngrams(line)
                    for ngram in ngrams:
                        self.letter_ngrams[ngram] += ngrams[ngram]
            f.close()

        for ngram in self.letter_ngrams:
            prefix = ngram[:self.key]
            if prefix not in self.letter_chain:
                self.letter_chain[prefix] = [ ]
            suffix = ngram[self.key:]
            for i in range(self.letter_ngrams[ngram]):
                self.letter_chain[prefix].append(suffix)

        self.letter_ngrams = {}

        pickle.dump(self.letter_chain, open(self.type + self.chain_filename_suffix, "wb" ))

    def get_word_ngrams(self, corpus):
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

    def generate_press_note(self, maxlength=100, note=list()):
        word_count = len(note)

        word_count += self.n - 1
        word = random.sample(self.word_chain.keys(), 1)[0]
        note += word.split()
        word = " ".join(note)
        while word_count < maxlength :
            if word in self.word_chain:
                # print(word, self.word_chain[word])
                word = random.sample(self.word_chain[word], 1)[0]
                note += word.split()
                word = " ".join(note[- self.key:])
            else:
                if 2 * word_count < maxlength:
                    # note[len(note) - 1] = note[len(note) - 1] + "."
                    note = self.generate_press_note(maxlength, note)
                break
            word_count += 1
        # return " ".join(note)
        return note

    def print_letter_stats(self, letter):
        stats = defaultdict(int)
        for i in self.letter_chain[letter]:
            stats[i] += 1
        print(letter, stats)

    def generate_word(self, maxlength=10):
        # word = random.choice(self.letter_chain[])
        # letter_count = 1
        # if len(word) == 0:
        word = random.sample(self.letter_chain.keys() , 1)[0]
        letter_count = self.key
        letters = word
        # print(word, letters)
        while letter_count < maxlength:
            if letters in self.letter_chain:
                # self.print_letter_stats(letters)
                letters = random.sample(self.letter_chain[letters], 1)[0]
                word += letters
                letters = word[- self.key:]
            else:
                break
            letter_count += 1

        return word


if __name__ == "__main__":
    # markov = MarkovChain('word', DATA_DIRECTORY + 'pap.txt', n=4, reload=False)
    # print(" ".join(markov.generate_press_note(100)))

    # markov = MarkovChain(TYPE_LETTER, DATA_DIRECTORY + 'pap.txt', n=4, reload=True)
    markov = MarkovChain(TYPE_LETTER, '../../data/lab3/formy.txt', n=4, reload=False)
    print(markov.generate_word(10))
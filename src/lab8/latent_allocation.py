import operator
import pickle
import re
import logging

from gensim import corpora, models, similarities
from lab8 import data_helpers
from sklearn.cluster import k_means


__author__ = 'Magda'

DATA_DIRECTORY = '../../data/lab8/'


class LatentAllocationModel:

    def __init__(self, document_file, encoding, model='LSA', similar_notes=5, topics_for_document=5, initialized=False):
        self.model_name = model
        self.similar_notes = similar_notes if similar_notes > 1 else 1
        self.topics_for_document = topics_for_document if topics_for_document > 1 else 1
        self.stop_list = "a, aby, ach, acz, aczkolwiek, aj, albo, ale, ależ, ani, aż, bardziej, bardzo, bo, bowiem, " \
                         "by, byli, bynajmniej, być, był, była, było, były, będzie, będą, cali, cała, cały, ci, cię, " \
                         "ciebie, co, cokolwiek, coś, czasami, czasem, czemu, czy, czyli, daleko, dla, dlaczego, " \
                         "dlatego, do, dobrze, dokąd, dość, dużo, dwa, dwaj, dwie, dwoje, dziś, dzisiaj, gdy, gdyby, " \
                         "gdyż, gdzie, gdziekolwiek, gdzieś, i, ich, ile, im, inna, inne, inny, innych, iż, ja, ją, " \
                         "jak, jakaś, jakby, jaki, jakichś, jakie, jakiś, jakiż, jakkolwiek, jako, jakoś, je, jeden, " \
                         "jedna, jedno, jednak, jednakże, jego, jej, jemu, jest, jestem, jeszcze, jeśli, jeżeli, już, " \
                         "ją, każdy, kiedy, kilka, kimś, kto, ktokolwiek, ktoś, która, które, którego, której, który, " \
                         "których, którym, którzy, ku, lat, lecz, lub, ma, mają, mało, mam, mi, mimo, między, mną, " \
                         "mnie, mogą, moi, moim, moja, moje, może, możliwe, można, mój, mu, musi, my, na, nad, nam, " \
                         "nami, nas, nasi, nasz, nasza, nasze, naszego, naszych, natomiast, natychmiast, nawet, nią, " \
                         "nic, nich, nie, niech, niego, niej, niemu, nigdy, nim, nimi, niż, no, o, obok, od, około, " \
                         "on, ona, one, oni, ono, oraz, oto, owszem, pan, pana, pani, po, pod, podczas, pomimo, " \
                         "ponad, ponieważ, powinien, powinna, powinni, powinno, poza, prawie, przecież, przed, " \
                         "przede, przedtem, przez, przy, roku, również, sama, są, się, skąd, sobie, sobą, sposób, " \
                         "swoje, ta, tak, taka, taki, takie, także, tam, te, tego, tej, temu, ten, teraz, też, to, " \
                         "tobą, tobie, toteż, trzeba, tu, tutaj, twoi, twoim, twoja, twoje, twym, twój, ty, tych, " \
                         "tylko, tym, u, w, wam, wami, was, wasz, wasza, wasze, we, według, wiele, wielu, więc, " \
                         "więcej, wszyscy, wszystkich, wszystkie, wszystkim, wszystko, wtedy, wy, właśnie, z, za, " \
                         "zapewne, zawsze, ze, zł, znowu, znów, został, żaden, żadna, żadne, żadnych, że, żeby".split(", ")
        self.ignored_characters = r"[\.,:;!?()\\/0-9\"\-\'+]"
        self.odm_ignored_characters = r"[\.\-\']"
        self.valid_model_names = { 'LSA', 'LDA' }

        self.note_number = 0
        self.dictionary = None
        self.corpus = None
        self.model = None
        self.note_id_map = []

        self.inflection_file = '../../data/odm.txt'
        # self.inflection_file = '../../data/lab7/inflection.pickle'

        # load data
        self.is_valid_call()
        self.inflection_dict = data_helpers.load_flexive_map(self.inflection_file, encoding='iso-8859-2',
                                                             ignored_characters=self.odm_ignored_characters)

        if initialized:
            self.dictionary = corpora.Dictionary.load(DATA_DIRECTORY + 'dictionary.dict')
            self.corpus = corpora.MmCorpus(DATA_DIRECTORY + 'corpus.mm')
            self.note_id_map = pickle.load(open(DATA_DIRECTORY + 'idmap.dict', 'rb'))
            if model == 'LSA':
                self.model = models.LsiModel.load(DATA_DIRECTORY + 'model.lsi')
            elif model == 'LDA':
                self.model = models.LdaModel.load(DATA_DIRECTORY + 'model.lda')
            self.index = similarities.MatrixSimilarity.load(DATA_DIRECTORY + 'similarity.index')
            print("Dictionary loaded: ")
            print(self.dictionary)
            print("Model loaded: ")
            print(self.model)
        else:
            self.initialize_data(document_file, encoding)
            print(self.dictionary)
            self.get_model()
            self.index = similarities.MatrixSimilarity(self.model[self.corpus])
            self.index.save(DATA_DIRECTORY + 'similarity.index')

    def is_valid_call(self):
        if not self.model_name in self.valid_model_names:
            raise ValueError("Invalid model name. Allowed model names are: " + ', '.join(self.valid_model_names))

    def initialize_data(self, notes_file, encoding):
        documents = []
        words = []
        note_id = -1
        with open(notes_file, encoding=encoding) as f:
            for line in f:
                if line.startswith("#"):
                    if note_id != -1:
                        documents.append(words)
                        self.note_id_map.append(note_id)
                    note_id = int(line[1:])
                    self.note_number += 1
                    words = []
                else:
                    words += self.normalize_text(line)
        self.dictionary = corpora.Dictionary(documents)
        self.remove_stop_words()
        self.dictionary.save(DATA_DIRECTORY + 'dictionary.dict')
        self.corpus = [self.dictionary.doc2bow(text) for text in documents]
        corpora.MmCorpus.serialize(DATA_DIRECTORY + 'corpus.mm', self.corpus, id2word=self.dictionary)
        with open(DATA_DIRECTORY + 'idmap.dict', 'wb') as handle:
            pickle.dump(self.note_id_map, handle)

    def normalize_text(self, text):
        words = []
        text = re.sub(self.ignored_characters, " ", text.lower().strip())
        splitted = text.split()
        for term in splitted:
            if term in self.inflection_dict:
                term = self.inflection_dict[term]
            words.append(term)
        return words

    def remove_stop_words(self):
        stop_ids = [ self.dictionary.token2id[stopword] for stopword in self.stop_list if stopword in
                     self.dictionary.token2id ]
        # once_ids = [tokenid for tokenid, docfreq in self.dictionary.dfs.iteritems() if docfreq == 1]
        self.dictionary.filter_tokens(stop_ids)     # remove stop words
        self.dictionary.compactify()

    def get_model(self):
        if self.model_name == 'LSA':
            self.model = models.lsimodel.LsiModel(self.corpus, id2word=self.dictionary, num_topics=100)
            self.model.save(DATA_DIRECTORY + 'model.lsi')
        elif self.model_name == 'LDA':
            self.model = models.ldamodel.LdaModel(self.corpus, id2word=self.dictionary, num_topics=100)
            self.model.save(DATA_DIRECTORY + 'model.lda')

    def find_similar_documents(self, text):
        vec_bow = self.dictionary.doc2bow(self.normalize_text(text))
        vec_lsi = self.model[vec_bow]   # convert the query to LSI space
        similar = self.index[vec_lsi]
        similar = sorted(enumerate(similar), key=operator.itemgetter(1), reverse=True)[:self.similar_notes]
        print("Similar documents" + str(similar))
        for (document_id, similarity) in similar:
            self.find_topics_for_id(document_id)

    def find_topics_for_id(self, document_id):
        print(document_id, self.note_id_map[document_id])
        vec_lsi = self.model[self.corpus[document_id]]
        # print(vec_lsi)
        top_topics = sorted(vec_lsi, key=operator.itemgetter(1), reverse=True)[
                     :self.topics_for_document]
        for (topic, score) in top_topics:
            print(self.model.print_topic(topic))

    def show_topics(self, n):
        self.model.print_topics(n)

    def run(self):
        main_menu_string = "\nType:\n\t" \
            "1 - type note to find similar ones and their topics\n\t" \
            "2 - show topics for given model\n"

        while True:
            print(main_menu_string)
            text = input(">> ")
            if text == "1" :
                print("Type your note:")
                text = input(">> ")
                self.find_similar_documents(text)
            elif text == "2" :
                print("Type how many topics should be shown:")
                text = input(">> ")
                try :
                    self.show_topics(int(text))
                except Exception:
                    pass
            else:
                print("Invalid option")


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    # lav = LatentAllocationModel('../../data/pap.txt', 'utf-8', 'LSA', initialized=True)
    lav = LatentAllocationModel('../../data/pap.txt', 'utf-8', 'LDA', initialized=True)
    lav.run()

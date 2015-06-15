from collections import defaultdict
import operator
import re
from lab4.cluster import WordMetric

__author__ = 'Magda'

DATA_DIRECTORY = '../../data/lab9/'
DOCUMENT_DIRECTORY = '../../data/'


class GraphModel:

    def __init__(self, document_file, encoding, order=3):
        self.order = order
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
        self.note_number = 0
        self.note_id_map = {}
        self.documents = {}
        self.corpus_nodes = {}
        self.corpus_graph = {}
        self.node_to_word_map = []
        self.word_to_node_map = {}
        self.vectorized_graph = []
        self.graph = None

        self.load_data(document_file, encoding)
        self.create_graph_structure()
        self.vectorize()
        # self.perform_clustering()

    def load_data(self, filename, encoding):
        note_id = 1
        documents = {}
        words = []
        with open(filename, encoding=encoding) as f:
           for line in f:
                if line.startswith("#"):
                    if note_id != -1:
                        words = [ word for word in words if word not in self.stop_list ]
                        documents[self.note_number] = words
                        self.note_id_map[self.note_number] = note_id

                    note_id = int(line[1:])
                    self.note_number += 1
                    words = []
                else:
                    line = re.sub(self.ignored_characters, " ", line)
                    words += line.lower().split()
        self.documents = documents
        # print(documents)

    def create_graph_structure(self):
        for document_id in self.documents:
            graph = self.create_graph(self.documents[document_id])
            self.corpus_graph[document_id] = graph

            # print(document_id)
            # print(graph)

    def create_graph(self, document):
        graph = {}

        # create node for each word in a document
        for word in set(document):
            if not word in self.word_to_node_map:
                self.word_to_node_map[word] = len(self.node_to_word_map)
                self.node_to_word_map.append(word)
            index = self.word_to_node_map[word]
            graph[index] = []

        # create verrices
        for index in range(len(document)):
            for k in range(self.order + 1):
                if index + k < len(document):
                    vertex1 = document[index]
                    vertex2 = document[index + k]
                    vertex1_index = self.word_to_node_map[vertex1]
                    vertex2_index = self.word_to_node_map[vertex2]
                    graph[vertex1_index].append(vertex2_index)

        return graph

    def vectorize(self):
        matrix = []
        for document_id in self.corpus_graph:
            subgraph = self.corpus_graph[document_id]
            vector = defaultdict(int)
            for vertex1 in subgraph:
                for vertex2 in subgraph[vertex1]:
                    if vertex1 < vertex2:
                        vector[(vertex1, vertex2)] += 1
                    else:
                        vector[(vertex2, vertex1)] += 1

            matrix.append(vector)
            # for vertex in subgraph:
            #     vector.append()
        self.matrix = matrix

    def find_similar_documents(self, document_id):
        main_vector = self.matrix[document_id]
        metric = WordMetric().cosine_metric

        index = 0
        similar_documents = []
        for vector in self.matrix:
            result = metric(main_vector, vector)
            similar_documents.append((result, index))
            index += 1

        similar_documents = sorted(similar_documents, key=operator.itemgetter(0))
        print(similar_documents[:10])
        for (score, index) in similar_documents[:10]:
            print(index, self.documents[index])

        return(similar_documents[:10])

    def run(self):
        while True:
            prompt = "\nType your document id: \n>> "
            document_id = input(prompt)
            self.find_similar_documents(int(document_id))


def gather_statistics(notes):
    with open(DATA_DIRECTORY + 'similar_results.txt', 'w+', encoding='utf-8') as f:
        for order in range(0, 5):
            print("Order :", order)

            graph_model = GraphModel(DOCUMENT_DIRECTORY + 'pap.txt', 'utf-8', order=order)

            for note in notes:
                similar_documents = graph_model.find_similar_documents(note)

                f.write("\n\nOrder %d, mote id: %d\n" % (order, note) )
                f.write("========================\n")
                f.writelines(["(%f, %d)," % (score, index) for (score, index) in similar_documents])
                f.write("\n")
                for (score, index) in similar_documents:
                    f.write("%d:\t" % index )
                    f.writelines(["%s, " % item for item in graph_model.documents[index]])
                    f.write("\n")
        f.flush()
        f.close()


if __name__ == "__main__":
    # graph_model = GraphModel(DOCUMENT_DIRECTORY + 'pap.txt', 'utf-8')
    # graph_model.run()

    notes = [ 1, 20, 21, 100, 16228, 18247, 28717, 13, 27, 28, 33, 36, 43, 46 ]
    gather_statistics(notes)



import functools

__author__ = 'Magda'

DATA_DIRECTORY = '../../data/lab4/'


class ClusterRank:

    def __init__(self, cluster_file=DATA_DIRECTORY + 'clusters.txt',
                 result_file=DATA_DIRECTORY + 'clusters_my.txt',
                 separator="##########"):
        self.cluster_file = cluster_file
        self.result_file = result_file
        self.separator = separator

    def precision(self, true_positives, false_positives, false_negatives):
        return 1.0 * true_positives / (true_positives + false_positives)

    def recall(self, true_positives, false_positives, false_negatives):
        return 1.0 * true_positives / (true_positives + false_negatives)

    def f1_precalc(self, precision, recall):
        return 2.0 * precision * recall / (precision + recall)

    def f1(self, true_positives, false_positives, false_negatives):
        precision = self.precision(true_positives, false_positives, false_negatives)
        recall = self.recall(true_positives, false_positives, false_negatives)
        return 2.0 * precision * recall / (precision + recall)

    def f1_compare(self, expected, result):
        true_positives = len(expected.intersection(result))
        precision = 1.0 * true_positives / len(result)
        recall = 1.0 * true_positives / len(expected)
        return (2.0 * precision * recall / (precision + recall), precision, recall)

    def read_clusters(self, file):
        clusters = {}
        current = set()
        with open(file) as f:
            for line in f.readlines():
                line = line.strip()
                if line.startswith('#'):
                    # Comment found, splitting sets
                    current = set()
                elif line:
                    current.add(line)
                    clusters[line] = current

        # for set2 in sets:
        #     print(sets[set2])
        return clusters

    def compare(self):
        proper_clusters = self.read_clusters(self.cluster_file)
        answer = self.read_clusters(self.result_file)

        results = []
        precision = []
        recall = []
        for line in proper_clusters:
            if line in answer:
                result = self.f1_compare(proper_clusters[line], answer[line])
            else:
                result = 0
            results.append(result[0])
            precision.append(result[1])
            recall.append(result[2])

        print('f1:', functools.reduce(lambda x, y: x + y, results) / len(results))
        print('precision:', functools.reduce(lambda x, y: x + y, precision) / len(precision))
        print('recall:', functools.reduce(lambda x, y: x + y, recall) / len(recall))


if __name__ == "__main__":
    rank = ClusterRank()
    rank.compare()
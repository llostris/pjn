from collections import defaultdict
import re

__author__ = 'Magda'


def load_flexive_map(flexive_forms_file, encoding, ignored_characters):
    inflection_dict = {}
    with open(flexive_forms_file, encoding=encoding) as f:
        for line in f:
            # print("AAA:" + line)
            splitted = line.lower().strip().split(", ")
            base_form = re.sub(ignored_characters, "", splitted[0])
            inflection_dict[splitted[0]] = base_form
            for form in splitted:
                form = form.strip()
                form = re.sub(ignored_characters, "", form)
                inflection_dict[form] = base_form
        f.close()
    print("Base form map loaded")

    return inflection_dict


if __name__ == '__main__':
    dictionary = load_flexive_map('../../data/odm.txt', encoding='iso-8859-2', ignored_characters=r"[\.\-\']")
    print('w.' in dictionary)
    print('w.' in dictionary.values())
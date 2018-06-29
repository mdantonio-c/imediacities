#!.venv/bin/python

from openpyxl import load_workbook
from datetime import datetime
from functools import reduce
import json

imc_namespace = 'https://imediacities.eu/resource/'
repls = (' ', '_'), ('/', '_')


def generate_iri(term):
    return imc_namespace + \
        reduce(lambda a, kv: a.replace(*kv), repls, term.strip())


wb = load_workbook('IMC-Vocabularies-Manual_Annotation-phase-2.xlsx')
vocabulary = {}
vocabulary['terms'] = []
vocabulary['vocabulary'] = "IMC controlled vocabulary"
vocabulary['created'] = str(datetime.now())
for ws in wb.worksheets:
    if ws.sheet_state == 'hidden':
        print('WARN: ignore hidden sheet: {}'.format(ws.title))
        continue
    # if ws.title != 'Persons(Gender)':
    #     continue
    # print('--- {} ---'.format(ws.title))
    vocabulary_class = {'label': ws.title.lower().capitalize(), 'children': []}

    # print('min row {}, max row {}'.format(ws.min_row, ws.max_row))
    current_group = ws['H2'].value
    group_terms = {}
    idx_count = 0
    for row_index in range(2, ws.max_row + 1):
        idx_count += 1
        en_term = ws['L' + str(row_index)].value
        # de_term = ws['K' + str(row_index)].value
        if en_term is None:
            # ignore groups without entry value
            continue
        en_term = en_term
        iri = ws['M' + str(row_index)].value
        if iri is None:
            iri = generate_iri(en_term)
        entry = {'id': iri, 'label': en_term}

        group = ws['I' + str(row_index)].value
        if group is not None:
            g = group.strip().capitalize()
            # print("adding entry to group '{}'".format(g))
            actual_terms = group_terms.get(g, None)
            if actual_terms is None:
                group_terms[g] = [entry]
            else:
                group_terms[g].append(entry)
        else:
            vocabulary_class['children'].append(entry)

    for key in group_terms:
        vocabulary_class['children'].append(
            {'label': key, 'children': group_terms[key]})
    vocabulary['terms'].append(vocabulary_class)

# json_data = json.dumps(vocabulary, indent=2)
# print(json_data)

with open('vocabulary.json', 'w') as f:
    json.dump(vocabulary, f, sort_keys=True, indent=2, ensure_ascii=False)

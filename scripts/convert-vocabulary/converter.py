#!.venv/bin/python

from openpyxl import load_workbook
from datetime import datetime
import json

wb = load_workbook('IMC-Vocabularies-Manual_Annotation-phase-2.xlsx')
vocabulary = {}
vocabulary['classes'] = []
vocabulary['vocabulary'] = "IMC controlled vocabulary"
vocabulary['created'] = str(datetime.now())
for ws in wb.worksheets:
    # if ws.title != 'Persons(Gender)':
    #     continue
    # print('--- {} ---'.format(ws.title))
    vocabulary_class = {'name': ws.title.lower(), 'groups': []}

    # print('min row {}, max row {}'.format(ws.min_row, ws.max_row))
    # for row in ws.iter_rows('A{}:A{}'.format(ws.min_row, ws.max_row), row_offset=1):
    # for row in ws['A2:A{}'.format(ws.max_row)]:
    current_group = ws['G2'].value
    group_terms = []
    for row_index in range(2, ws.max_row + 1):
        entry = ws['J' + str(row_index)].value
        group = ws['G' + str(row_index)].value
        if entry is None:
            # ignore also groups without entry value
            continue
        if group != current_group:
            # save the existing group
            # print('\\__{}'.format(current_group))
            vocabulary_class['groups'].append({'name': current_group, 'terms': group_terms})
            current_group = group
            # group is changed
            group_terms = []

        group_terms.append(entry)
        # print('\t-{}'.format(entry))

    # flush last group
    vocabulary_class['groups'].append({'name': current_group, 'terms': group_terms})

    # groups = set([ws['G' + str(i)].value for i in range(2, ws.max_row)])
    # vocabulary_class['groups'] = list(filter(None.__ne__, groups))
    vocabulary['classes'].append(vocabulary_class)

# json_data = json.dumps(vocabulary, indent=2)
# print(json_data)

with open('vocabulary.json', 'w') as f:
    json.dump(vocabulary, f, sort_keys=True, indent=2, ensure_ascii=False)

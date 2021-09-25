# %%
import json
import re

dataset_json = []

def load_dataset_json():
    global dataset_json
    dataset_json = []
    with open('dataset.json') as infile: # 샘플 문제
        dataset_json = json.load(infile)
        # print(dataset_json)

    re_number = '[0-9]+(\.[0-9]+)?(\/[0-9]+(\.[0-9]+)?)?'

    for q in dataset_json:
        print(' ')
        if 'question' not in q:
            continue
        strlist = []
        if 'equation' in q:
            if type(q['equation']) is not list:
                q['equation'] = [q['equation']]
            for str in q['equation']:
                strlist.extend(re.findall(r'\b[^\d\W]+\b', str))
                for match in re.compile(re_number).finditer(str):
                    strlist.append(match.group())
        if 'code' in q:
            if type(q['code']) is not list:
                q['code'] = [q['code']]
            for str in q['code']:
                strlist.extend(re.findall(r'\b[^\d\W]+\b', str))
                for match in re.compile(re_number).finditer(str):
                    strlist.append(match.group())

        strset = set(strlist)
        strset.discard('print')
        strset.discard('equ')
        strset.discard('argmin')
        strset.discard('argmax')
        strset.discard('len')
        strset.discard('min')
        strset.discard('max')
        strset.discard('math')
        strlist = list(strset)
        # print(strlist)

        q['template_values'] = strlist

        template = q['question']
        for idx, str in enumerate(strlist):
            template = re.sub(r'^' + str, f'var{idx}', template)
            template = re.sub(r' ' + str, f' var{idx}', template)
        q['template'] = template
   
        q['template_equation'] = []
        if 'equation' in q:
            for eq in q['equation']:
                for idx, str in enumerate(strlist):
                    eq = re.compile('\\b' + str + '\\b').sub(f'var{idx}', eq)
                    # eq = re.sub(r'\b' + str + r'\b', f'<{idx}>', eq)
                q['template_equation'].append(eq)

        q['template_code'] = []
        if 'code' in q:
            for eq in q['code']:
                for idx, str in enumerate(strlist):
                    eq = re.compile('\\b' + str + '\\b').sub(f'var{idx}', eq)
                    # eq = re.sub(r'\b' + str + r'\b', f'<{idx}>', eq)
                q['template_code'].append(eq)

        print(q['template'])
        print(q['template_equation'])
        print(q['template_code'])
        print(q['template_values'])

# %%
print('loading dataset...', end=' ')
load_dataset_json()
print('done.')

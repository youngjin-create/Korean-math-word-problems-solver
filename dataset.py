# %%
import json
import re
import utils

dataset_json = []

def find_literals(line, question):
    strlist = []

    # line이 통채로 equation에 포함된 경우, 예) 수식 1A+2B=C3
    if line in question:
        strlist.append(line)

    # 단어
    strlist.extend(re.findall(r'\b[^\d\W]+\b', line))

    # 숫자
    re_number = '[0-9]+(\.[0-9]+)?(\/[0-9]+(\.[0-9]+)?)?'
    for match in re.compile(re_number).finditer(line):
        strlist.append(match.group())

    strset = set(strlist)
    return strset

def build_template(q):
    print(' ')
    if 'question' not in q:
        print('empty question error.')
        return

    q['question_preprocessed'] = utils.preprocess(q['question'])
    strlist = []
    strset = set()
    if 'equation' in q:
        if type(q['equation']) is not list:
            q['equation'] = [q['equation']]
        for line in q['equation']:
            strset |= find_literals(line, q['question_preprocessed'])
    if 'code' in q:
        if type(q['code']) is not list:
            q['code'] = [q['code']]
        for line in q['code']:
            strset |= find_literals(line, q['question_preprocessed'])

    strset.discard('print')
    strset.discard('equ')
    strset.discard('argmin')
    strset.discard('argmax')
    strset.discard('len')
    strset.discard('min')
    strset.discard('max')
    strset.discard('math')
    strlist = list(strset)
    strlist.sort(key=len)
    strlist.reverse()

    re_number = '[0-9]+(\.[0-9]+)?(\/[0-9]+(\.[0-9]+)?)?'
    strtypes = [None] * len(strlist)
    for idx, str in enumerate(strlist):
        if '=' in str:
            strtypes[idx] = 'equation'
        elif re.fullmatch(re_number, str):
            strtypes[idx] = 'number'
        else:
            strtypes[idx] = 'string'

    q['template_values'] = strlist

    template = q['question_preprocessed']
    for idx, str in enumerate(strlist):
        template = re.sub('^' + re.escape(str), f'var{idx}', template)
        template = re.sub(' ' + re.escape(str), f' var{idx}', template)
    q['template'] = template

    q['template_equation'] = []
    if 'equation' in q:
        for eq in q['equation']:
            for idx, str in enumerate(strlist):
                eq = re.compile(r'\b' + re.escape(str) + r'\b').sub(f'var{idx}', eq)
            q['template_equation'].append(eq)

    q['template_code'] = []
    if 'code' in q:
        for eq in q['code']:
            for idx, str in enumerate(strlist):
                eq = re.compile(r'\b' + re.escape(str) + r'\b').sub(f'var{idx}', eq)
            q['template_code'].append(eq)

    print(q['template'])
    print(q['template_equation'])
    print(q['template_code'])
    print(q['template_values'])

def load_dataset_json():
    global dataset_json
    dataset_json = []
    with open('dataset.json') as infile: # 샘플 문제
        dataset_json = json.load(infile)
        # print(dataset_json)

    for q in dataset_json:
        build_template(q)
        

# %%
print('loading dataset...', end=' ')
load_dataset_json()
print('done.')

# %%
import json
import re

# %%
# '<x:숫자>'와 같은 입력이 들어왔을 때 (x, 숫자)를 리턴
def get_name_and_type(item):
    # str_types = ['숫자', '수열', '지시자', '지시자들', '미지수', '미지수들', '사람', '사람들', '과목', '과목들']
    pos = item.find(':')
    first, second = (item[1:pos], item[pos+1:-1]) if pos != -1 else ('', item[1:-1])
    return (first, second) if second.upper() == second.lower() else (second, first)

# %%
fast_dataset = dict()
dataset = []
dataset_json = []

def load_dataset():
    global fast_dataset
    global dataset
    fast_dataset = dict()
    dataset = []

    mode = ''
    current_data = []
    for line in open('dataset.txt', 'r').readlines():
        if line[0] == '#':
            continue
        elif line[0] == ':':
            # data['statements'].append(line[1:].strip())
            for data in current_data:
                data['statements'].append(line[1:].strip())
            mode = 'statement'
        elif len(line.strip()) > 0:
            pos = line.find('=>')
            phrase = line[:pos].strip() if pos != -1 else line.strip()
            reduces_to = line[pos+2:].strip() if pos != -1 else None
            to_compare = phrase
            matches = []
            children = []
            # print(phrase)
            for match in re.compile('<.*?>').finditer(phrase):
                matches.append(match)
                children.append(get_name_and_type(match.group()))
            for match in reversed(matches):
                to_compare = phrase[:match.span()[0]] + '<' + get_name_and_type(match.group())[1] + '>' + to_compare[match.span()[1]:]
            # print(to_compare)
            data = { 'P': phrase, 'C': to_compare, 'R': reduces_to, 'children': children, 'Ctypes': ''.join([x[1] for x in children]), 'statements': [] }
            dataset.append(data)
            if mode != 'phrase':
                current_data = []
            current_data.append(data)
            mode = 'phrase'

    for data in dataset:
        t = data['Ctypes']
        if not(t in fast_dataset):
            fast_dataset[t] = []
        fast_dataset[t].append(data)

def load_dataset_json():
    global dataset_json
    dataset_json = []
    with open('dataset.json') as infile: # 샘플 문제
        dataset_json = json.load(infile)
        # print(dataset_json)

    for q in dataset_json:
        print(' ')
        if 'question' not in q:
            continue
        strlist = []
        if 'equation' in q:
            if type(q['equation']) is not list:
                q['equation'] = [q['equation']]
            for eq in q['equation']:
                strlist.extend(re.findall(r'\b\w+\b', eq))
        if 'code' in q:
            if type(q['code']) is not list:
                q['code'] = [q['code']]
            for code in q['code']:
                strlist.extend(re.findall(r'\b\w+\b', code))

        strset = set(strlist)
        strset.discard('print')
        strset.discard('equ')
        strset.discard('argmin')
        strset.discard('len')
        strset.discard('min')
        strset.discard('max')
        strset.discard('math')
        strlist = list(strset)
        print(strlist)

        template = q['question']
        for idx, str in enumerate(strlist):
            template = re.sub(r'^' + str, f'[{idx}]', template)
            template = re.sub(r' ' + str, f' [{idx}]', template)

        q['template_equation'] = []
        if 'equation' in q:
            for eq in q['equation']:
                for idx, str in enumerate(strlist):
                    eq = re.compile('\\b' + str + '\\b').sub(f'[{idx}]', eq)
                    # eq = re.sub(r'\b' + str + r'\b', f'<{idx}>', eq)
                q['template_equation'].append(eq)

        q['template_code'] = []
        if 'code' in q:
            for eq in q['code']:
                for idx, str in enumerate(strlist):
                    eq = re.compile('\\b' + str + '\\b').sub(f'[{idx}]', eq)
                    # eq = re.sub(r'\b' + str + r'\b', f'<{idx}>', eq)
                q['template_code'].append(eq)

        q['template'] = template
        print(q['template'])
        print(q['template_equation'])
        print(q['template_code'])

# %%
print('loading dataset...', end=' ')
load_dataset()
load_dataset_json()
print('done.')

# %%

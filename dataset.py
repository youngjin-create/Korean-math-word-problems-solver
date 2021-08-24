# %%
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

# %%
print('loading dataset...', end=' ')
load_dataset()
print('done.')

# %%

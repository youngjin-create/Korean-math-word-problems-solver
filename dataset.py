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

    # 풀이 과정에서 literal을 추출하여 문제를 템플릿화
    strset = set()
    field_names = ['equation', 'code', 'objective']
    for fn in field_names:
        if fn in q:
            if type(q[fn]) is not list:
                q[fn] = [q[fn]]
            for line in q[fn]:
                strset |= find_literals(line, q['question_preprocessed'])

    discard_keywords = ['x', 'print', 'argmin', 'argmax', 'len', 'min', 'max', 'math']
    for k in discard_keywords:
        strset.discard(k)

    strlist = list(strset)
    strlist.sort(key=len)
    strlist.reverse()
    q['template_values'] = strlist

    re_number = '[0-9]+(\.[0-9]+)?(\/[0-9]+(\.[0-9]+)?)?'
    strtypes = [None] * len(strlist)
    for idx, str in enumerate(strlist):
        if '=' in str:
            strtypes[idx] = 'equation'
        elif re.fullmatch(re_number, str):
            strtypes[idx] = 'number'
        else:
            strtypes[idx] = 'string'
    q['template_types'] = strtypes

    template = q['question_preprocessed']
    for idx, str in enumerate(strlist):
        template = re.sub('^' + re.escape(str), f'var{idx}', template)
        template = re.sub(' ' + re.escape(str), f' var{idx}', template)
    q['template'] = template

    for fn in field_names:
        q['template_'+fn] = []
        if fn in q:
            for eq in q[fn]:
                for idx, str in enumerate(strlist):
                    eq = re.compile(r'\b' + re.escape(str) + r'\b').sub(f'var{idx}', eq)
                q['template_'+fn].append(eq)

    # 추가된 필드 출력
    print(q['template'])
    print(q['template_equation'])
    print(q['template_code'])
    print(q['template_objective'])
    print(q['template_values'])
    print(q['template_types'])

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

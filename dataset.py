# %%
import json
import csv
import re
import utils

dataset_json = []
dataset_csv = []

def find_literals(line, question):
    strlist = []

    # line이 통채로 equation에 포함된 경우, 예) 수식 1A+2B=C3
    if line in question and len(line) > 0:
        strlist.append(line)

    # 단어
    strlist.extend(re.findall(r'\b[^\d\W]+\b', line))

    # 숫자
    re_number = r'[0-9]+([.][0-9]+)?(/[0-9]+([.][0-9]+)?)?' #'[0-9]+(\.[0-9]+)?(\/[0-9]+(\.[0-9]+)?)?'
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

    q['question_pruning'] = utils.pruning_vector(q['question_preprocessed'])

    q['template_lists'], q['question_preprocessed'] = utils.extract_lists(q['question_preprocessed'])

    # 풀이 과정에서 literal을 추출하여 문제를 템플릿화
    strset = set()
    field_names = ['equation', 'code', 'objective']
    for fn in field_names:
        if fn not in q:
            continue
        if type(q[fn]) is not list:
            q[fn] = [q[fn]]
        for line in q[fn]:
            strset |= find_literals(line, q['question_preprocessed'])

    discard_keywords = ['vars', 'x', 'print', 'argmin', 'argmax', 'len', 'min', 'max', 'math', 'floor']
    for k in discard_keywords:
        strset.discard(k)

    # 추출해낸 literal 중에서 question에 나오지 않는 것들은 상수항이므로 리스트에서 제외
    strlist = list(strset)
    strlist.sort(key=len)
    strlist.reverse()
    strlist[:] = [x for x in strlist if len(re.findall(r'(^|\s)(' + re.escape(x) + r')($|\D)', q['question_preprocessed'])) > 0]
    q['template_values'] = strlist
    q['template_types'] = [utils.literal_type(x) for x in strlist]

    template = q['question_preprocessed']
    for idx, str in enumerate(strlist):
        template = re.sub(r'(^|\s)(' + re.escape(str) + r')($|\D)', f'\\g<1>@{idx}\\g<3>', template)
    q['template'] = template

    for fn in field_names:
        q['template_'+fn] = []
        if fn not in q:
            continue
        for eq in q[fn]:
            for idx, str in enumerate(strlist):
                eq = re.compile(r'(^|[^@])(\b' + re.escape(str) + r'\b)').sub(f'\\g<1>@{idx}', eq)
            q['template_'+fn].append(eq)

    # # 추가된 필드 출력
    # print(q['template'])
    # print(q['template_lists'])
    # print(q['template_equation'])
    # print(q['template_code'])
    # print(q['template_objective'])
    # print(q['template_values'])
    # print(q['template_types'])

def load_dataset_json():
    global dataset_json
    dataset_json = []
    with open('dataset.json') as infile: # 샘플 문제
        dataset_json = json.load(infile)
        # print(dataset_json)

    for q in dataset_json:
        build_template(q)

def load_dataset_csv():
    global dataset_csv
    dataset_csv = []
    with open('dataset.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row[0]=='유형':
                continue
            q = dict(question=row[1], type=row[0], answer=row[3], equation=row[6], code=row[7], objective=row[8])
            dataset_csv.append(q)
            # print(q)
            
    for q in dataset_csv:
        build_template(q)

# %%
print('loading dataset...', end=' ')
load_dataset_json()
load_dataset_csv()
print('done.')

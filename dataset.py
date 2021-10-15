# %%
import json
import csv
import re
import utils

dataset_json = []

def find_literals(line, question):
    strlist = []

    # @#$ + 숫자
    strlist.extend(re.findall(r'[@#$][ns]?\d+\b', line))

    # 단어, 숫자제외
    strlist.extend(re.findall(r'\b[^\d\W]+\b', line))

    # 숫자, @#$으로 시작하지 않는 경우만
    re_number = r'(^|[^@#$])([0-9]+([.][0-9]+)?(/[0-9]+([.][0-9]+)?)?)' #'[0-9]+(\.[0-9]+)?(\/[0-9]+(\.[0-9]+)?)?'
    for match in re.compile(re_number).finditer(line):
        strlist.append(match.group(2))

    strset = set(strlist)
    return strset

def build_template(q):
    # print(' ')
    if 'question' not in q:
        print('empty question error.')
        return

    q['question_preprocessed'] = utils.preprocess(q['question'])

    q['question_pruning'] = utils.pruning_vector(q['question_preprocessed'])

    q['extracted_lists'], q['question_preprocessed'] = utils.extract_lists(q['question_preprocessed'])
    q['extracted_equations'], q['question_preprocessed'] = utils.extract_equations(q['question_preprocessed'])

    # if len(q['extracted_lists']) > 0 or len(q['extracted_equations']) > 0:
    #     print(q['question'])
    #     print(q['question_preprocessed'])
    #     print(q['extracted_lists'])
    #     print(q['extracted_equations'])

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
    # wildcard dictionary
    wcs = dict()
    for s in strlist:
        if s[0] in ['@', '#', '$']:
            wcs[s] = s
        else:
            prefix = '@n' if utils.literal_type(s) == 'number' else '@s'
            idx = 0
            while prefix+f'{idx}' in wcs.keys():
                idx += 1
            wcs[prefix+f'{idx}'] = s
    q['template_wildcards'] = wcs

    # q['template_values'] = strlist
    # q['template_types'] = [utils.literal_type(x) for x in strlist]

    template = q['question_preprocessed']
    for key in q['template_wildcards']:
        template = re.sub(r'(^|\s)(' + re.escape(q['template_wildcards'][key]) + r')($|\D)', f'\\g<1>{key}\\g<3>', template)
    # for idx, str in enumerate(strlist):
    #     template = re.sub(r'(^|\s)(' + re.escape(str) + r')($|\D)', f'\\g<1>@{idx}\\g<3>', template)
    q['template'] = template

    for fn in field_names:
        q['template_'+fn] = []
        if fn not in q:
            continue
        for eq in q[fn]:
            for key in q['template_wildcards']:
                eq = re.sub(r'(^|[^@])(\b' + re.escape(q['template_wildcards'][key]) + r'\b)', f'\\g<1>{key}', eq)
            # for idx, str in enumerate(strlist):
            #     eq = re.compile(r'(^|[^@])(\b' + re.escape(str) + r'\b)').sub(f'\\g<1>@{idx}', eq)
            q['template_'+fn].append(eq)

    q['template_tags'] = utils.pos_tagging(q['template'])

    # # 추가된 필드 출력
    # print(q['template'])
    # print(q['template_lists'])
    # print(q['template_equation'])
    # print(q['template_code'])
    # print(q['template_objective'])
    # print(q['template_values'])
    # print(q['template_types'])
    return

def load_dataset_json():
    global dataset_json
    dataset_json = []
    with open('dataset.json') as infile: # 샘플 문제
        dataset_json = json.load(infile)
        # print(dataset_json)

    for q in dataset_json:
        build_template(q)

def load_dataset_csv(filename):
    # global dataset_csv
    dataset_csv = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            q = dict(id=row[0], type=row[1], question_original=row[2], question=row[3], answer=row[5], equation=row[8], code=row[9], objective=row[10])
            if q['id'] == 'ID' or q['question'] == '':
                continue
            dataset_csv.append(q)
            # print(q)
            
    for q in dataset_csv:
        build_template(q)

    return dataset_csv

# %%
print('loading dataset...', end=' ')
# load_dataset_json()
dataset_csv = load_dataset_csv('dataset.csv')
# dataset_csv_qanda = load_dataset_csv('dataset_qanda.csv')
datasets_all = [dataset_csv] #, dataset.dataset_csv_qanda] # 사용할 데이터셋

print('done.')

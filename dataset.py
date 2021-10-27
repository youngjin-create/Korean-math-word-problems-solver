# %%
import json
import csv
import re

import utils
import tagging
import dataset_google_sheets
import pickle

dataset_json = []

def is_Korean_number(w):
    return w in ['삼', '사', '오', '육', '칠', '팔', '구', '십', '십', '십이', '십삼', '십사', '십오', '십육', '십칠', '십팔', '십구', '이십']

def find_literals(line, question):
    strlist = []

    # @#$ + 숫자
    strlist.extend(re.findall(r'[@#$][ns]?\d+\b', line))

    # 단어, 숫자제외
    strlist.extend(re.findall(r'\b[^\d\W]+\b', line))

    # 숫자, 괄호로 묶인 경우만
    re_number = r'(\()([0-9]+([.][0-9]+)?(/[0-9]+([.][0-9]+)?)?)(\))' #'[0-9]+(\.[0-9]+)?(\/[0-9]+(\.[0-9]+)?)?'
    for match in re.compile(re_number).finditer(line):
        strlist.append(match.group(2))

    strset = set([x for x in strlist if is_Korean_number(x) == False])
    return strset

def find_KorNumSpecial(line): # (삼) (사) (오) 특별처리
    strset = set()
    for match in re.finditer(r'(\()(삼|사|오|육|칠|팔|구|십|십일|십이|십삼|십사|십오|십육|십칠|십팔|십구|이십)(\))', line):
        strset.add(match.group(2))
    return strset

def build_template(q, is_phrase=False):
    # print(' ')
    if 'question' not in q or q['question'] == '':
        # print('empty question error.')
        return False

    # q['question_preprocessed'] = utils.preprocess(q['question'])
    # q['question_pruning'] = utils.pruning_vector(q['question_preprocessed'])
    # q['question_predefined_patterns'], q['question_preprocessed'] = utils.extract_predefined_patterns(q['question_preprocessed'])

    q['question_predefined_patterns'], q['question_preprocessed'] = utils.extract_predefined_patterns(q['question'])
    q['question_preprocessed'] = utils.preprocess(q['question_preprocessed'])
    q['question_pruning'] = utils.pruning_vector(q['question_preprocessed'])

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

    discard_keywords = ['vars', 'x', 'print', 'argmin', 'argmax', 'len', 'min', 'max', 'math', 'floor', 'True', 'False']
    for k in discard_keywords:
        strset.discard(k)

    # 추출해낸 literal 중에서 question에 나오지 않는 것들은 상수항이므로 리스트에서 제외
    strlist = list(strset)
    strlist.sort(key=len)
    strlist.reverse()
    strlist[:] = [x for x in strlist if len(re.findall(r'(^|\s)(' + re.escape(x) + r')($|\D)', q['question_preprocessed'])) > 0]
    # wildcard dictionary
    wcs, wcs_rev = dict(), dict()
    for s in strlist:
        if s[0] in ['@', '#', '$']:
            wcs[s] = s
            wcs_rev[s] = s
        else:
            prefix = '@n' if utils.literal_type(s) in ['number', 'variable'] else '@s'
            idx = 0
            while prefix+f'{idx}' in wcs.keys():
                idx += 1
            wcs[prefix+f'{idx}'] = s
            wcs_rev[s] = prefix+f'{idx}'
    q['template_wildcards'] = wcs

    template = q['question_preprocessed']
    for key in q['template_wildcards']:
        template = re.sub(r'(^|\s)(' + re.escape(q['template_wildcards'][key]) + r')($|\D)', f'\\g<1>{key}\\g<3>', template)
    q['template'] = template

    Kornumset = set()
    for fn in field_names:
        if fn not in q:
            continue
        for line in q[fn]:
            Kornumset |= find_KorNumSpecial(line) # (삼) (사) (오) 특별처리

    for s in Kornumset:
        prefix = '@n'
        idx = 0
        while prefix+f'{idx}' in wcs.keys():
            idx += 1
        wcs[prefix+f'{idx}'] = s
        wcs_rev[s] = prefix+f'{idx}'

    for fn in field_names:
        q['template_'+fn] = []
        if fn not in q:
            continue
        for eq in q[fn]:
            for key in q['template_wildcards']:
                # eq = re.sub(r'(?!([@#$]|@n|@s))(\b' + re.escape(q['template_wildcards'][key]) + r'\b)', f'\\g<1>{key}', eq)
                eq = re.sub(r'(^|[^@#$])(\b' + re.escape(q['template_wildcards'][key]) + r'\b)', f'\\g<1>{key}', eq)
            q['template_'+fn].append(eq)

    # wildcard 치환으로 인해서 tag 정보가 잘못 추출되는 경우가 발생, 원래 문장을 이용해서 추출한 tag으로 수정해준다.
    q['template_tags'] = tagging.pos_tagging(q['template'])
    original_tags = tagging.pos_tagging(utils.preprocess(q['question_original']))
    score, assignments, correspondence, _ = tagging.match_to_template_tags(q['template_tags'], original_tags)
    for c in correspondence:
        if c[0] <= 0 or c[1] <= 0:
            continue
        if q['template_tags'][c[0]-1][0] == original_tags[c[1]-1][0]:
            if q['template_tags'][c[0]-1][1] not in ['WILDCARD', 'WILDCARD_NUM', 'WILDCARD_STR', 'NUMBER', 'STRING', 'EQUATION', 'NUMBERS', 'STRINGS', 'MAPPING']:
                tag = list(q['template_tags'][c[0]-1])
                tag[1] = original_tags[c[1]-1][1]
                q['template_tags'][c[0]-1] = tuple(tag)

    for idx in range(0, len(q['template_tags'])):
        for n in Kornumset:
            tag = q['template_tags'][idx]
            if tag[0] == n+'각형' or tag[0] == n+'면체' or tag[0] == n+'각뿔' or tag[0] == n+'각기둥' or tag[0] == '정'+n+'각형' or tag[0] == '정'+n+'면체':
                tag = list(q['template_tags'][idx])
                q['template'] = q['template'].replace(tag[0], tag[0].replace(n, wcs_rev[n]))
                tag[1] = 'WILDCARD_OBJECT_' + tag[0].replace(n, '_n_')
                tag[0] = wcs_rev[n]
                q['template_tags'][idx] = tuple(tag)
    
    if is_phrase:
        q['template_tags'] = tagging.add_paddings(q['template_tags'])
        # q['template_tags'] = [('', 'PADDING', 0, 0), *q['template_tags'], ('', 'PADDING', 0, 0)]
        
    return True

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
            if q['id'] == 'ID' or (q['question_original'] == '' and q['question'] == ''):
                continue
            dataset_csv.append(q)
            # print(q)
            
    for q in dataset_csv:
        build_template(q)

    return dataset_csv

def load_dataset_google_sheets(sheetname, is_phrase=False):
    dataset = dataset_google_sheets.load_dataset(sheetname)
    
    for q in dataset:
        if q['question'] == '':
            q['question'] = q['question_original']
        if not build_template(q, is_phrase):
            del dataset[q]

    return dataset


# %%
print('loading dataset...', end=' ')


############# LOADING DATA from PICKLE ###############
with open('data.pickle', 'rb') as f:
    loaded_data = pickle.load(f)
dataset_sentences = loaded_data['dataset_sentences']
dataset_phrases = loaded_data['dataset_phrases']

# ############### LOADING DATA from GOOGLE SHEETS #############
# dataset_google_sentences_teacher = load_dataset_google_sheets('선생님문제모음')
# dataset_google_sentences_elementary = load_dataset_google_sheets('콴다초등문제모음')
# dataset_google_sentences_augmented = load_dataset_google_sheets('augmented')
# dataset_google_phrases1 = load_dataset_google_sheets('수찾기3', is_phrase=True)
# dataset_google_phrases2 = load_dataset_google_sheets('크기비교', is_phrase=True)
# # load_dataset_json()
# # dataset_csv = load_dataset_csv('dataset.csv')
# # dataset_csv_qanda = load_dataset_csv('dataset_qanda.csv')
# # datasets_all = [dataset_csv] #, dataset.dataset_csv_qanda] # 사용할 데이터셋

# dataset_sentences = []
# dataset_sentences.extend(dataset_google_sentences_teacher)
# dataset_sentences.extend(dataset_google_sentences_elementary)
# dataset_sentences.extend(dataset_google_sentences_augmented)
# dataset_phrases = []
# dataset_phrases.extend(dataset_google_phrases1)
# dataset_phrases.extend(dataset_google_phrases2)

# ############### SAVE DATA #############
# loaded_data = { 
#     'dataset_sentences' : dataset_sentences,
#     'dataset_phrases' : dataset_phrases
# }
# with open('data.pickle', 'wb') as f:
#     pickle.dump(loaded_data, f, pickle.HIGHEST_PROTOCOL)


print('done.')

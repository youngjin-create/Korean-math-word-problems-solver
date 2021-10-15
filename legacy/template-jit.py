# %%
from numba import jit

import time
import re
import wordsim
import utils
import dataset

import numpy as np

# pos tagging된 두 단어를 비교한 score를 계산, w1 = template tag, w2 = question tag
# w = (str, POS, start, end)의 형식, start, end는 문장에서의 span 시작과 끝 index
# 이상적으로는 str과 POS값을 모두 고려하여 score를 계산하여야 하지만 일단 POS값을 중요시하여 계산
# POS값에 따른 score matrix를 생각할 수 있고, 이것을 자동학습 할 수 있으면 좋을듯
# @jit(nopython=True)
def match_word_tags(w1, w2): 
    if w1[1] == w2[1]: # POS가 같으면 페널티 없음
        return 0.0
    if w1[1] == 'NONE' or w2[1] == 'NONE': # 매칭되는 단어가 없어서 스킵할 경우
        return 0.6
    if w1[1] == 'WILDCARD':
        if w2[1][0] == 'N' or w2[1] == 'SL': # WILDCARD는 단어 또는 숫자에 매칭 가능
            return 0.0
        else:
            return 1000000.0#float('inf')
    if w1[1] == 'SF' or w2[1] == 'SF': # 마침표
        return 0.1
    # POS가 다른 단어끼리 매칭
    return 1.0

# score_table = 1000000.0 * np.ones([100, 100])
# # scores = np.zeros([100, 100])
# scores = np.random.random([100, 100])
# tracks1 = -1000000.0 * np.ones([100, 100])
# tracks2 = -1000000.0 * np.ones([100, 100])

# @jit(nopython=True)
# 문장 비교, 비슷할 수록 낮은 값 리턴
def match_to_template_tags_jit(len_t, len_q, score_table, scores, tracks1, tracks2):
    # # score_table = [[1000000.0 for i in range(len(question_tags)+1)] for j in range(len(template_tags)+1)]
    # # assign_table = [['' for i in range(len(question_tags)+1)] for j in range(len(template_tags)+1)]
    # for repeat in range(10):
    #     for i1 in range(0, len(template_tags)+1):
    #         for i2 in range(0, len(question_tags)+1):
    #             # score_table[i1][i2] = match_word_tags(
    #             #     template_tags[i1-1] if i1>0 else ('', 'NONE', None, None),
    #             #     question_tags[i2-1] if i2>0 else ('', 'NONE', None, None))
    #             t_tag = template_tags[i1-1] if i1>0 else ('', 'NONE', -1, -1)
    #             q_tag = question_tags[i2-1] if i2>0 else ('', 'NONE', -1, -1)
    #             if t_tag[1] == q_tag[1]: # POS가 같으면 페널티 없음
    #                 s = 0.0
    #             elif t_tag[1] == 'NONE' or q_tag[1] == 'NONE': # 매칭되는 단어가 없어서 스킵할 경우
    #                 s = 0.6
    #             elif t_tag[1] == 'WILDCARD':
    #                 if q_tag[1][0] == 'N' or q_tag[1] == 'SL': # WILDCARD는 단어 또는 숫자에 매칭 가능
    #                     s = 0.0
    #                 else:
    #                     s = 1000000.0
    #             elif t_tag[1] == 'SF' or q_tag[1] == 'SF': # 마침표
    #                 s = 0.1
    #             # POS가 다른 단어끼리 매칭
    #             else:
    #                 s = 1.0
    #             score_table[i1][i2] = s
    #             # scores[i1, i2] = 0.0

    # scores: question_tags[0:i1]과 template_tags[0:i2]를 매칭한 최적 스코어

    # return 1, 1
    # scores = [[1000000.0 for i in range(len(question_tags)+1)] for j in range(len(template_tags)+1)]
    # tracks1 = [[-1000000 for i in range(len(question_tags)+1)] for j in range(len(template_tags)+1)]
    # tracks2 = [[-1000000 for i in range(len(question_tags)+1)] for j in range(len(template_tags)+1)]
    for i1 in range(0, len_t+1):
        for i2 in range(0, len_q+1):
            scores[i1,i2], tracks1[i1][i2], tracks2[i1][i2] = 1000000.0, -1000000, -1000000
            if i1>0 and i2>0 and scores[i1,i2] > scores[i1-1,i2-1] + score_table[i1][i2]:
                scores[i1,i2] = scores[i1-1,i2-1] + score_table[i1][i2]
                tracks1[i1][i2] = i1-1
                tracks2[i1][i2] = i2-1
            if i2>0 and scores[i1,i2] > scores[i1,i2-1] + score_table[0][i2]:
                scores[i1,i2] = scores[i1,i2-1] + score_table[0][i2]
                tracks1[i1][i2] = i1
                tracks2[i1][i2] = i2-1
            if i1>0 and scores[i1,i2] > scores[i1-1,i2] + score_table[i1][0]:
                scores[i1,i2] = scores[i1-1,i2] + score_table[i1][0]
                tracks1[i1][i2] = i1-1
                tracks2[i1][i2] = i2
            if i1==0 and i2==0:
                scores[i1,i2], tracks1[i1][i2], tracks2[i1][i2] = 0.0, -1000000, -1000000

    return scores, tracks1, tracks2
    return scores[-1][-1], 1
    correspondence = []
    assignments = dict()
    i1, i2 = len(template_tags), len(question_tags)
    while True:
        if i1 == -1000000 or i2 == -1000000:
            break
        if tracks1[i1][i2] == i1 - 1 and tracks2[i1][i2] == i2 - 1: # 실제 tags사이에 매칭이 일어난 경우 (None과 매칭되지 않고) WILDCARD에 대응되는 값을 assignments에 추가
            if template_tags[i1-1][1] == 'WILDCARD':
                name = template_tags[i1-1][0][1:]
                # if name not in assignments:
                #     assignments[name] = set()
                # assignments[name].add(question_tags[i2-1])
                assignments[name] = question_tags[i2-1]
        correspondence.append((i1, i2, scores[i1,i2]))
        i1, i2 = tracks1[i1][i2], tracks2[i1][i2]
    # def backtrack(i1, i2):
    #     if i1 == -1000000 or i2 == -1000000:
    #         return
    #     if tracks1[i1][i2] == i1 - 1 and tracks2[i1][i2] == i2 - 1: # 실제 tags사이에 매칭이 일어난 경우 (None과 매칭되지 않고) WILDCARD에 대응되는 값을 assignments에 추가
    #         if template_tags[i1-1][1] == 'WILDCARD':
    #             name = template_tags[i1-1][0][1:]
    #             # if name not in assignments:
    #             #     assignments[name] = set()
    #             # assignments[name].add(question_tags[i2-1])
    #     correspondence.append((i1, i2, scores[i1][i2]))
    #     backtrack(tracks1[i1][i2], tracks2[i1][i2])
    # backtrack(len(template_tags), len(question_tags))
    # return scores[-1][-1], assignments
    # return scores[-1][-1], assignments

    if visualize:
        last = (0, 0, 0.0)
        for i in range(len(correspondence), 0, -1):
            match = correspondence[i-1]
            left = template_tags[match[0]-1] if match[0] > last[0] else (' ', 'NONE', -1, -1)
            right = question_tags[match[1]-1] if match[1] > last[1] else (' ', 'NONE', -1, -1)
            print((' (' + left[0] + ' ' + left[1] + ') --- (' + right[0] + ' ' + right[1] + ')', match[2] - last[2]))
            last = match
        print(('matching score = ', scores[-1,-1]))

    return scores[-1,-1], assignments

# match_to_template_tags(utils.pos_tagging('상자 안에 5개의 감이 있습니다.'), utils.pos_tagging('상자 안에 5개의 감이 있습니다.'))
# match_to_template_tags(utils.pos_tagging('상자 안에 @0개의 감이 있습니다.'), utils.pos_tagging('박스 안에 5개의 과일이 있다.'))

# @jit(nopython=True)
# def test_func(score_table, scores, tracks1, tracks2, visualize=False):
    
#     return 1, 1

def match_to_template_tags(template_tags, question_tags, visualize=False):
    len_t, len_q = len(template_tags)+1, len(question_tags)+1
    score_table = 1000000.0 * np.ones([len_t+1, len_q+1])
    for i1 in range(0, len(template_tags)+1):
        for i2 in range(0, len(question_tags)+1):
            # score_table[i1][i2] = match_word_tags(
            #     template_tags[i1-1] if i1>0 else ('', 'NONE', None, None),
            #     question_tags[i2-1] if i2>0 else ('', 'NONE', None, None))
            t_tag = template_tags[i1-1] if i1>0 else ('', 'NONE', -1, -1)
            q_tag = question_tags[i2-1] if i2>0 else ('', 'NONE', -1, -1)
            if t_tag[1] == q_tag[1]: # POS가 같으면 페널티 없음
                s = 0.0
            elif t_tag[1] == 'NONE' or q_tag[1] == 'NONE': # 매칭되는 단어가 없어서 스킵할 경우
                s = 0.6
            elif t_tag[1] == 'WILDCARD':
                if q_tag[1][0] == 'N' or q_tag[1] == 'SL': # WILDCARD는 단어 또는 숫자에 매칭 가능
                    s = 0.0
                else:
                    s = 1000000.0
            elif t_tag[1] == 'SF' or q_tag[1] == 'SF': # 마침표
                s = 0.1
            # POS가 다른 단어끼리 매칭
            else:
                s = 1.0
            score_table[i1][i2] = s
            # scores[i1, i2] = 0.0

    scores = np.zeros([len_t+1, len_q+1])
    tracks1 = -1000000.0 * np.ones([len_t+1, len_q+1])
    tracks2 = -1000000.0 * np.ones([len_t+1, len_q+1])
    scores, tracks1, tracks2 = match_to_template_tags_jit(len_t, len_q, score_table, scores, tracks1, tracks2)

    correspondence = []
    assignments = dict()
    i1, i2 = len_t, len_q
    while True:
        if i1 == -1000000 or i2 == -1000000:
            break
        if tracks1[i1][i2] == i1 - 1 and tracks2[i1][i2] == i2 - 1: # 실제 tags사이에 매칭이 일어난 경우 (None과 매칭되지 않고) WILDCARD에 대응되는 값을 assignments에 추가
            if template_tags[i1-1][1] == 'WILDCARD':
                name = template_tags[i1-1][0][1:]
                if name not in assignments:
                    assignments[name] = set()
                assignments[name].add(question_tags[i2-1])
                # assignments[name] = question_tags[i2-1]
        correspondence.append((i1, i2, scores[i1,i2]))
        i1, i2 = tracks1[i1][i2], tracks2[i1][i2]

    if visualize:
        last = (0, 0, 0.0)
        for i in range(len(correspondence), 0, -1):
            match = correspondence[i-1]
            left = template_tags[match[0]-1] if match[0] > last[0] else (' ', 'NONE', -1, -1)
            right = question_tags[match[1]-1] if match[1] > last[1] else (' ', 'NONE', -1, -1)
            print((' (' + left[0] + ' ' + left[1] + ') --- (' + right[0] + ' ' + right[1] + ')', match[2] - last[2]))
            last = match
        print(('matching score = ', scores[-1,-1]))

    return scores[-1,-1], assignments

def find_closest(problem):
    closest_distance, best_pattern, best_assignments = float('inf'), None, None
    datasets = [dataset.dataset_csv, dataset.dataset_csv_qanda] # 사용할 데이터셋
    dists = []
    for dset in datasets:
        for template in dset:
            if utils.is_pruning(template['question_pruning'], problem['pruning_vector']):
                continue
            if template['extracted_lists'].keys() != problem['extracted_lists'].keys():
                continue
            if (len(template['extracted_equations']) > 0) != (len(problem['extracted_equations']) > 0):
                continue
            # distance, assignments = match_to_template(problem['question_preprocessed'], template)
            distance, assignments = match_to_template_tags(template['template_tags'], problem['question_tags'])
            if distance < closest_distance:
                closest_distance, best_pattern, best_assignments = distance, template, assignments

            dists.append([distance, template, assignments])
            # if distance < 10:
            #     template = template['template']
            #     print(f'    matching distance = {distance}')
            #     print(f'    matching template = {template}')
            #     print(f'    matching assignments = {assignments}')

    problem['closest_k'] = sorted(dists, key=lambda x: x[0])[:10]

    return closest_distance, best_pattern, best_assignments

def find_template(problem):
    problem['pruning_vector'] = utils.pruning_vector(problem['question_preprocessed'])
    # 문제에서 숫자열이나 문자열 패턴이 발견되면 추출해내고, 추출한 부분을 제외한 문장으로 매칭을 시도한다.
    problem['extracted_lists'], problem['question_preprocessed'] = utils.extract_lists(problem['question_preprocessed'])
    problem['extracted_equations'], problem['question_preprocessed'] = utils.extract_equations(problem['question_preprocessed'])

    problem['question_tags'] = utils.pos_tagging(problem['question_preprocessed'])

    # question = problem['question_preprocessed']
    distance, matched, assignments = find_closest(problem)

    print(f'best match distance = {distance}')
    print(f'best match template = {matched}')
    print(f'best match template candidate assigments = {assignments}')
    values = [x for x in matched['template_values']]
    # for idx, valueset in enumerate(assignments):
    #     if len(valueset) > 0:
    #         values[idx] = list(valueset)[0]
    for key in assignments:
        assignments[key] = list(assignments[key])[0][0]
    print(f'best match template final assigments = {values}')
    print('extracted question lists = ' + str(problem['extracted_lists']))
    print('extracted question equations = ' + str(problem['extracted_equations']))

    # problem['extracted_lists'] = extracted_lists
    # problem['extracted_equations'] = extracted_equations
    problem['best_template_distance'] = distance
    problem['best_template'] = matched
    problem['best_template_assignment'] = assignments

    # 매칭된 템플릿을 이용하여 statements(lists, equation, code, objective) 구성
    # statements는 풀이과정과 답안을 구하기 위한 충분정보가 포함되어야 한다.
    statements = dict()
    field_names = ['equation', 'code', 'objective']
    for fn in field_names:
        statements[fn] = []
    if problem['extracted_lists']:
        if 'numbers' in problem['extracted_lists']:
            statements['code'].append('numbers=' + str(problem['extracted_lists']['numbers']))
        if 'strings' in problem['extracted_lists']:
            statements['code'].append('strings=' + str(problem['extracted_lists']['strings']))
    if problem['extracted_equations']:
        for eq in problem['extracted_equations']:
            statements['equation'].append(eq)
    for fn in field_names:
        if 'template_'+fn not in matched:
            continue
        for line in matched['template_'+fn]:
            for key in assignments:
                line = re.sub(f'(@{key})($|\D)', assignments[key] + '\\g<2>', line)
                # line = re.sub(f'\\b@{idx}\\b', v, line)
            statements[fn].append(line)

    print(f'statements = {statements}')
    problem['statements'] = statements

    return distance, statements

# %%
# score, assignments = match_to_template_tags(
#     utils.pos_tagging('비행기에 @0명이 타고 있습니다. 그 중 @1명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?'),
#     utils.pos_tagging('버스에 22명이 타고 있습니다. 그 중 118명이 내렸을 때, 버스에 남아있는 있는 사람은 얼마입니까?'),
#     visualize=True)
# score, assignments = match_to_template_tags(
#     utils.pos_tagging('비행기에 351명이 타고 있습니다. 그 중 158명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?'),
#     utils.pos_tagging('달력에서 31일까지 있는 연속 된 2달 중, 더 나중에 있는 달은 언제 입니까?'),
#     visualize=True)
# score, assignments = match_to_template_tags(utils.pos_tagging('상자 안에 @0개의 감이 있습니다.'), utils.pos_tagging('박스 안에 5개의 과일이 있다.'), visualize=True)
# score, assignments = match_to_template_tags(
#     utils.pos_tagging('@strings 각각 1개씩 있습니다. 이 중 @1개를 택하여 1개의 접시에 담으려고 합니다. @2과 @0을 함께 담지 않는 방법은 모두 몇 가지입니까?'),
#     utils.pos_tagging('@strings 각각 1개씩 있습니다. 이 중 3개를 택하여 한 개의 접시에 담으려고 합니다. 포도와 귤을 함께 담지 않는 방법은 모두 몇 가지입니까?'),
#     visualize=True)
# score, assignments = match_to_template_tags(
#     utils.pos_tagging('@strings 각각 1개씩 있습니다. 이 중 @1개를 택하여 $1개의 접시에 담으려고 합니다. @3과 @0을 함께 담지 않는 방법은 모두 몇 가지입니까?'),
#     utils.pos_tagging('@strings 각각 1개씩 있습니다. 이 중 3개를 택하여 한 개의 접시에 담으려고 합니다. 감과 귤을 함께 담지 않는 방법은 모두 몇 가지입니까?'),
#     visualize=True)

score, assignments = match_to_template_tags(
    utils.pos_tagging('비행기에 @0명이 타고 있습니다. 그 중 @1명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?'),
    utils.pos_tagging('@strings 각각 1개씩 있습니다. 이 중 3개를 택하여 한 개의 접시에 담으려고 합니다. 감과 귤을 함께 담지 않는 방법은 모두 몇 가지입니까?'),
    visualize=True)

start_time = time.time()
for i in range(1000):
    # utils.pos_tagging('비행기에 @0명이 타고 있습니다. 그 중 @1명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?')
    # utils.pos_tagging('@strings 각각 1개씩 있습니다. 이 중 3개를 택하여 한 개의 접시에 담으려고 합니다. 감과 귤을 함께 담지 않는 방법은 모두 몇 가지입니까?')
    # score, assignments = match_to_template_tags(
    #     utils.pos_tagging('비행기에 @0명이 타고 있습니다. 그 중 @1명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?'),
    #     utils.pos_tagging('@strings 각각 1개씩 있습니다. 이 중 3개를 택하여 한 개의 접시에 담으려고 합니다. 감과 귤을 함께 담지 않는 방법은 모두 몇 가지입니까?'))
    score, assignments = match_to_template_tags(
        utils.pos_tagging('비행기에 @0명이 타고 있습니다. 그 중 @1명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?'),
        utils.pos_tagging('버스에 22명이 타고 있습니다. 그 중 118명이 내렸을 때, 버스에 남아있는 있는 사람은 얼마입니까?'))
print(time.time() - start_time)
# score, assignments = match_to_template_tags(
#     utils.pos_tagging('비행기에 @0명이 타고 있습니다. 그 중 @1명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?'),
#     utils.pos_tagging('@strings 각각 1개씩 있습니다. 이 중 3개를 택하여 한 개의 접시에 담으려고 합니다. 감과 귤을 함께 담지 않는 방법은 모두 몇 가지입니까?'),
#     visualize=True)
# print(score)
# print(assignments)

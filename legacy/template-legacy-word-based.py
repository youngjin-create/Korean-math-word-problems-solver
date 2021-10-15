# %%
import re
import wordsim
import utils
import dataset

re_var_ending = re.compile(r'(@[0-9]+)(\D*)')
re_number = re.compile(r'([0-9]+([.][0-9]+)?(/[0-9]+([.][0-9]+)?)?)')

def match_word(w1, type, w2): # w1 = template word, w2 = question word
    global re_var_ending
    global re_number
    match = re_var_ending.fullmatch(w1)
    if match: # template 단어가 wildcard를 포함하고 있으면
        ending = match[2]
        if utils.compare_ending(w2[len(w2)-len(ending):], ending):
            return 0, w2[:len(w2)-len(ending)]
        if type == 'number':
            num = re_number.findall(w2)
            if num == []:
                return float('inf'), ''
            else:
                return 0, num[0][0]
        return 1-wordsim.ko_model.wv.similarity(w1, w2), w2
    else: # 단순 단어 비교
        if w1 == w2:
            return 0, None
        return 1-wordsim.ko_model.wv.similarity(w1, w2), None
    return

def match_word_pos(w1, type, w2): # w1 = template word, w2 = question word
    global re_var_ending
    global re_number
    match = re_var_ending.fullmatch(w1)
    if match: # template 단어가 wildcard를 포함하고 있으면
        ending = match[2]
        if utils.compare_ending(w2[len(w2)-len(ending):], ending):
            return 0, w2[:len(w2)-len(ending)]
        if type == 'number':
            num = re_number.findall(w2)
            if num == []:
                return float('inf'), ''
            else:
                return 0, num[0][0]
        return 1-wordsim.ko_model.wv.similarity(w1, w2), w2
    else: # 단순 단어 비교
        if w1 == w2:
            return 0, None
        pos1, pos2 = utils.pos_tagging(w1), utils.pos_tagging(w2)
        # if len(pos1) == len(pos2):
        if ' '.join([tag for (str, tag) in pos1]) == ' '.join([tag for (str, tag) in pos2]):
            return 0.1, None
        return 1-wordsim.ko_model.wv.similarity(w1, w2), None
    return

# 문장 비교, 비슷할 수록 낮은 값 리턴
def match_to_template(question, template): # template, question sentence, values
    global re_var_ending
    skip_penalty_question = 0.6
    skip_penalty_template = 0.6
    # skip_penalty = 0.6

    values = template['template_values']
    types = template['template_types']

    wt, wq = template['template'].split(' '), question.split(' ')

    varnum, vartype = [None] * len(wt), [None] * len(wt)
    for i in range(0, len(wt)):
        match = re_var_ending.fullmatch(wt[i]) # 템플릿의 단어가 '@num'으로 시작하는 경우
        if match:
            varnum[i] = int(match[1][1:])
            vartype[i] = types[varnum[i]]

    score_table = [[float('inf') for i in range(len(wq))] for j in range(len(wt))]
    assign_table = [['' for i in range(len(wq))] for j in range(len(wt))]
    for i1 in range(0, len(wt)):
        for i2 in range(0, len(wq)):
            # score_table[i1][i2], assign_table[i1][i2] = match_word(wt[i1], vartype[i1], wq[i2])
            score_table[i1][i2], assign_table[i1][i2] = match_word_pos(wt[i1], vartype[i1], wq[i2])
            if vartype[i1] != None and utils.literal_type(assign_table[i1][i2]) != vartype[i1]:
                score_table[i1][i2], assign_table[i1][i2] = float('inf'), ''

    scores = [[float('inf') for i in range(len(wq)+1)] for j in range(len(wt)+1)]
    for i in range(len(wq)+1):
        scores[0][i] = i * skip_penalty_question
    scores[0][0] = 0
    for j in range(1, len(wt)+1):
        if varnum[j-1] != None:
            scores[j][0] = float('inf')
        else:
            scores[j][0] = scores[j-1][0] + skip_penalty_template
    tracks = [[(None, None) for i in range(len(wq)+1)] for j in range(len(wt)+1)]

    for i1 in range(0, len(wt)):
        for i2 in range(0, len(wq)):
            if varnum[i1] != None: # @num, 매칭되는 단어가 꼭 있어야 함
                scores[i1+1][i2+1] = scores[i1][i2] + score_table[i1][i2]
                tracks[i1+1][i2+1] = (i1, i2)
            else: # just words
                scores[i1+1][i2+1] = scores[i1][i2] + score_table[i1][i2]
                tracks[i1+1][i2+1] = (i1, i2)
                if scores[i1+1][i2+1] > scores[i1+1][i2] + skip_penalty_template:
                    scores[i1+1][i2+1] = scores[i1+1][i2] + skip_penalty_template
                    tracks[i1+1][i2+1] = (i1+1, i2)
                if scores[i1+1][i2+1] > scores[i1][i2+1] + skip_penalty_question:
                    scores[i1+1][i2+1] = scores[i1][i2+1] + skip_penalty_question
                    tracks[i1+1][i2+1] = (i1, i2+1)

    assignments = [set() for i in range(len(values))]
    def backtrack(i1, i2):
        if i1 < 0 or i2 < 0:
            return
        if varnum[i1] != None and assign_table[i1][i2]:
            assignments[varnum[i1]].add(assign_table[i1][i2])
        backtrack(tracks[i1+1][i2+1][0]-1, tracks[i1+1][i2+1][1]-1)
    backtrack(len(wt)-1, len(wq)-1)

    return scores[len(wt)][len(wq)], assignments
    # print(score(len(wt)-1, len(wq)-1))
    # print(table)
    # print(wt)
    # print(wq)
    # return score(len(wt)-1, len(wq)-1) # / (len(wt) + len(wq))

def find_closest(problem):

    closest_distance, best_pattern, best_assignments = float('inf'), None, None
    # for p in dataset.dataset_json:
    #     if utils.is_pruning(p['question_pruning'], problem['pruning_vector']) or p['template_lists'] != extracted_lists.keys:
    #         continue
    #     distance, assignments = match_to_template(question, p)
    #     if distance < closest_distance:
    #         closest_distance, best_pattern, best_assignments = distance, p, assignments
    for template in dataset.dataset_csv:
        if utils.is_pruning(template['question_pruning'], problem['pruning_vector']):
            continue
        if template['extracted_lists'].keys() != problem['extracted_lists'].keys():
            continue
        if (len(template['extracted_equations']) > 0) != (len(problem['extracted_equations']) > 0):
            continue
        distance, assignments = match_to_template(problem['question_preprocessed'], template)
        if distance < closest_distance:
            closest_distance, best_pattern, best_assignments = distance, template, assignments
        if distance < 5:
            template = template['template']
            print(f'    matching distance = {distance}')
            print(f'    matching template = {template}')
            print(f'    matching assignments = {assignments}')

    return closest_distance, best_pattern, best_assignments

def find_template(problem):
    problem['pruning_vector'] = utils.pruning_vector(problem['question_preprocessed'])
    # 문제에서 숫자열이나 문자열 패턴이 발견되면 추출해내고, 추출한 부분을 제외한 문장으로 매칭을 시도한다.
    problem['extracted_lists'], problem['question_preprocessed'] = utils.extract_lists(problem['question_preprocessed'])
    problem['extracted_equations'], problem['question_preprocessed'] = utils.extract_equations(problem['question_preprocessed'])

    # question = problem['question_preprocessed']
    distance, matched, assignments = find_closest(problem)

    print(f'best match distance = {distance}')
    print(f'best match template = {matched}')
    print(f'best match template candidate assigments = {assignments}')
    values = [x for x in matched['template_values']]
    for idx, valueset in enumerate(assignments):
        if len(valueset) > 0:
            values[idx] = list(valueset)[0]
    print(f'best match template final assigments = {values}')
    print('extracted question lists = ' + str(problem['extracted_lists']))
    print('extracted question equations = ' + str(problem['extracted_equations']))

    # problem['extracted_lists'] = extracted_lists
    # problem['extracted_equations'] = extracted_equations
    problem['best_template_distance'] = distance
    problem['best_template'] = matched
    problem['best_template_assignment'] = values

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
            for idx, v in enumerate(values):
                line = re.sub(f'(@{idx})($|\D)', v + '\\g<2>', line)
                # line = re.sub(f'\\b@{idx}\\b', v, line)
            statements[fn].append(line)

    print(f'statements = {statements}')
    problem['statements'] = statements

    return distance, statements

# %%
# match_to_template(
#     '비행기에 351명이 타고 있습니다. 그 중 158명이 내렸습니다. 비행기에 타고 있는 인원은 얼마입니까?',
#     dict(template='버스에 22명이 타고 있습니다. 그 중 118명이 내렸습니다. 버스에 타고 있는 인원은 얼마입니까?', template_values=[]*0, template_types=['number']*0))

    
match_to_template(
    '선물 한 개를 포장하는 데 색 테이프가 5/8m가 필요합니다.',
    dict(template='선물 상자 한 개를 포장하는 데 색 테이프가 0.84m 필요합니다.', template_values=[]*0, template_types=['number']*0))
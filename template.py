# %%
import re
import numpy as np

import utils
import dataset
import tagging

def find_closest(problem):
    closest_distance, best_pattern, best_assignments = float('inf'), None, None
    dists = []
    for template in dataset.dataset_sentences:
        if utils.is_pruning(template['question_pruning'], problem['pruning_vector']):
            continue
        if template['question_predefined_patterns']['lists'].keys() != problem['question_predefined_patterns']['lists'].keys():
            continue
        if (len(template['question_predefined_patterns']['equations']) > 0) != (len(problem['question_predefined_patterns']['equations']) > 0):
            continue
        # distance, assignments = match_to_template(problem['question_preprocessed'], template)
        distance, assignments, _ = tagging.match_to_template_tags(template['template_tags'], problem['question_tags'])
        if distance < closest_distance:
            closest_distance, best_pattern, best_assignments = distance, template, assignments

        dists.append([distance, template, assignments])

    problem['closest_k'] = sorted(dists, key=lambda x: x[0])[:10]

    return closest_distance, best_pattern, best_assignments

def find_phrases(problem):
    len_q = len(problem['question_tags'])
    matches = [[(float('inf'), None, None) for i in range(0, len_q+1)] for j in range(0, len_q+1)]
    for template in dataset.dataset_phrases:
        distance, assignments, correspondence = tagging.match_to_template_tags(template['template_tags'], problem['question_tags'])
        span = [1, 2]
        if distance < matches[span[0]][span[1]][0]:
            matches[span[0]][span[1]] = (distance, template, assignments)

    return
    # return closest_distance, best_pattern, best_assignments

def match(problem):
    problem['pruning_vector'] = utils.pruning_vector(problem['question_preprocessed'])

    problem['question_predefined_patterns'], problem['question_preprocessed'] = utils.extract_predefined_patterns(problem['question_preprocessed'])

    problem['question_tags'] = tagging.pos_tagging(problem['question_preprocessed'])

    distance, matched, assignments = find_closest(problem)
    # find_phrases(problem)

    print(f'best match distance = {distance}')
    print(f'best match template = {matched}')
    print(f'best match template candidate assigments = {assignments}')
    for key in assignments:
        assignments[key] = list(assignments[key])[0][0]
    print(f'best match template final assigments = {assignments}')
    print('extracted predefined patterns = ' + str(problem['question_predefined_patterns']))

    problem['best_template_distance'] = distance
    problem['best_template'] = matched
    problem['best_template_assignment'] = assignments

    # 매칭된 템플릿을 이용하여 statements(lists, equation, code, objective) 구성
    # statements는 풀이과정과 답안을 구하기 위한 충분정보가 포함되어야 한다.
    statements = dict()
    field_names = ['equation', 'code', 'objective']
    for fn in field_names:
        statements[fn] = []
    if problem['question_predefined_patterns']:
        for key in problem['question_predefined_patterns']['lists']:
            statements['code'].append(key + '=' + str(problem['question_predefined_patterns']['lists'][key]))
        for eq in problem['question_predefined_patterns']['equations']:
            statements['equation'].append(eq)
    for fn in field_names:
        if 'template_'+fn not in matched:
            continue
        for line in matched['template_'+fn]:
            for key in assignments:
                line = re.sub(f'({re.escape(key)})($|\D)', assignments[key] + '\\g<2>', line)
            statements[fn].append(line)

    print(f'statements = {statements}')
    problem['statements'] = statements

    return distance, statements
